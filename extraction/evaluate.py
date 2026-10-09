from pathlib import Path
from typing import List,Union,Dict
from itertools import pairwise

import langextract as lx
import langextract.core.data as lxdata
import dataclasses
from collections import defaultdict
import pandas as pd 
import copy
import spacy
import yaml

nlp = spacy.blank("en")

def overlaps(a, b):
    return a.start_pos < b.end_pos and b.start_pos < a.end_pos

def is_exact(a, b):
    return a.start_pos == b.start_pos and a.end_pos == b.end_pos

def is_subspan(a, b):
    return b.start_pos <= a.start_pos and b.end_pos >= a.end_pos

def is_superspan(a, b):
    return a.start_pos <= b.start_pos and a.end_pos >= b.end_pos

def intersection_over_union(a,b):
    intersection = min(a.end_pos, b.end_pos) - max(a.start_pos, b.start_pos)
    
    if intersection <= 0: return 0
    
    union = max(a.end_pos, b.end_pos) - min(a.start_pos, b.start_pos)
    return intersection/union

from collections import Counter

def compute_token_score(p, g):
    # 1. Tokenize the strings and lowercase them for fair comparison
    pred_tokens = [token.text.lower() for token in nlp.make_doc(p.strip())]
    gold_tokens = [token.text.lower() for token in nlp.make_doc(g.strip())]
    if not pred_tokens or not gold_tokens:
        return {"token_p": 0.0, "token_r": 0.0}
        
    pred_counts = Counter(pred_tokens)
    gold_counts = Counter(gold_tokens)
    overlap = pred_counts & gold_counts
    # The '&' operator on Counters takes the minimum count of shared elements
    true_positives = sum(overlap.values())
    
    precision = true_positives / len(pred_tokens)
    recall = true_positives / len(gold_tokens)
    return {"token_p": precision, "token_r": recall}

def avg(elems):
    n = len(elems)
    if n == 0:return 0
    return sum(elems)/n

def overlap_length(a, b):
    return max(0, min(a.end_pos, b.end_pos) - max(a.start_pos, b.start_pos))

def classify_match(gt_span, pred_span):
    if is_exact(gt_span, pred_span):
        return "Exact", 4
    if is_subspan(gt_span, pred_span):
        return "Subspan", 3
    if is_superspan(gt_span, pred_span):
        return "Superspan", 2
    if overlaps(gt_span, pred_span):
        return "Partial", 1
    return None

def ensure_sorted(extractions, label):
    if not all(
        (left.char_interval.start_pos, left.char_interval.end_pos)
        <= (right.char_interval.start_pos, right.char_interval.end_pos)
        for left, right in pairwise(extractions)
    ):
        raise ValueError(f"{label} must be sorted by char interval incrementally")
    
@dataclasses.dataclass(kw_only=True)
class EvaluatedDocument(lxdata.AnnotatedDocument):

    gt_extractions: List[lxdata.Extraction]
    matched_extractions: Dict[int, List[lxdata.Extraction]] = dataclasses.field(default_factory=lambda: defaultdict(list))

    @classmethod
    def from_annotated(
        cls,
        doc: lxdata.AnnotatedDocument,
        ground_truth: List[lxdata.Extraction],
    ) -> "EvaluatedDocument":
        edoc = cls(
            extractions=doc.extractions,
            text=doc.text,
            gt_extractions=ground_truth,
        )
        edoc.document_id=doc.document_id
        return edoc
    
    def __post_init__(self):
        idx = 0
        last_search_pos = 0
        
        # check if GT extractions are fully inside the text and populate missing fields
        for extraction in self.gt_extractions:
            self.matched_extractions[idx] = []

            # remove newlines at the end to account for yaml nits
            extraction.extraction_text = extraction.extraction_text.rstrip()
            try:
                start = self.text.index(extraction.extraction_text,last_search_pos)
                end = start + len(extraction.extraction_text)
            except ValueError as e:
                raise ValueError(f"""
                training sample is not an exact match!
                File: {self.document_id}
                Ground truth:\n\t{extraction}
                """) from e
                
            extraction.extraction_index = idx 
            extraction.alignment_status = lxdata.AlignmentStatus.MATCH_EXACT
            extraction.char_interval = lxdata.CharInterval(start,end)
            
            last_search_pos = end
            # do not follow langextract, they start at one
            idx += 1

        """
        Grounding: LLMs may occasionally extract content from few-shot examples rather than the input text. LangExtract automatically detects this: extractions that cannot be located in the source text will have char_interval = None. Filter these out with [e for e in result.extractions if e.char_interval] to keep only grounded results.
        """
        original_size = len(self.extractions)
        self.extractions = [e for e in self.extractions if e.char_interval]
        if len(self.extractions) != original_size:
            pass
            #("Warning: LLM suffered from unlocatabled extraction")
        self.extractions.sort(key=lambda x:(x.char_interval.start_pos,x.char_interval.end_pos))
        self.gt_extractions.sort(key=lambda x:(x.char_interval.start_pos,x.char_interval.end_pos))

        # match extraction to ground truth
        current_idx = 0
        for extraction in self.extractions:
            # edge case: some extraction have a null attribute, some an empty dict, some an dict with _unsed
            if extraction.attributes is None:
                extraction.attributes = dict()
            pred_span = extraction.char_interval

            while (
                current_idx < len(self.gt_extractions)
                and pred_span.start_pos >= self.gt_extractions[current_idx].char_interval.end_pos
            ):
                current_idx += 1

            matched = False
            check_idx = current_idx
            while (
                check_idx < len(self.gt_extractions)
                and self.gt_extractions[check_idx].char_interval.start_pos < pred_span.end_pos
            ):
                current = self.gt_extractions[check_idx]
                if overlaps(pred_span, current.char_interval):
                    self.matched_extractions[check_idx].append(extraction)
                    # keep track of spans assigned to multiple ground truth spans
                    extraction.attributes["counter"] = extraction.attributes.get("counter",0) + 1
                    matched = True
                check_idx += 1

            if not matched:
                self.matched_extractions[None].append(extraction)

class Evaluator:
    def __init__(self, experiment_path : Union[str,Path],stage : str = "test",suffix : str = "",overwrite_training : Union[str,Path] | None = None):
        self.experiment_path = Path(experiment_path)
        self.stage = stage
        
        if not self.experiment_path.exists(): raise ValueError(f"{self.experiment_path} does not exist")
        extractions_path = self.experiment_path / "outputs" / f"result-{stage}{suffix}.jsonl"
        
        if overwrite_training is not None:
            ground_truth_path = Path(overwrite_training)
        else:
            ground_truth_path = self.experiment_path / f"{stage}.yaml"
            
        if not extractions_path.exists(): raise ValueError(f"{extractions_path} does not exist")
        if not ground_truth_path.exists(): raise ValueError(f"{ground_truth_path} does not exist")
        
        annotated_docs = lx.io.load_annotated_documents_jsonl(extractions_path,show_progress = False)
        with ground_truth_path.open("r") as f:
            test_documents = yaml.safe_load(f)
            if not isinstance(test_documents,dict):
                raise ValueError(f"Set {ground_truth_path} has no high level dict! Do you use a .yaml file?")
            
            for file,extraction in test_documents.items():
                if not isinstance(extraction,dict) or "extractions" not in  extraction:
                    raise ValueError(f"{file} has no extractions dictionary {extraction}")
                if not isinstance(extraction["extractions"],list):
                    raise ValueError(f"{file} has invalid extractions {extraction}")
                    
        self.documents = []

        for document in annotated_docs:
            file = document.document_id.strip()
            if file not in test_documents:
                continue
            
            tests = test_documents[file]
            self.documents.append(
                EvaluatedDocument.from_annotated(document,[lxdata.Extraction(**(args)) for args in tests["extractions"]])
            )
        
        if len(self.documents) != len(test_documents):
            diff = set(test_documents.keys()).difference(doc.document_id for doc in self.documents)
            raise ValueError(f"Expected {len(test_documents)} but only found {len(self.documents)} documents:\n\t{'\n\t'.join(diff)}")
        
    def evaluate_per_extraction(self):
        rows = []
        for document in self.documents:
            for t_index,predictions in document.matched_extractions.items():
                # we only look at single matches of true positves
                if t_index is None or len(predictions) != 1:
                    continue
                    
                t = document.gt_extractions[t_index].char_interval
                p = predictions[0].char_interval
                metric = 1 - intersection_over_union(t,p)
                diff_t = t.end_pos - t.start_pos
                diff_p = p.end_pos - p.start_pos
                
                if diff_t >= diff_p:
                    # smaller match
                    metric *= -1
                    
                rows.append({
                    "file" : document.document_id,
                    "IoU" : metric,
                    "Size_ref" : diff_t, 
                    "Size_pre" : diff_p,
                    "Size_text" : len(predictions[0].extraction_text),
                    "Size_ratio" : round((diff_p-diff_t) / diff_t,2),
                    "Alignment" : predictions[0].alignment_status.value
                })
        return rows 
    
    def fuzzy_pairs(self):
        rows = []
        for document in self.documents:
            for _,predictions in document.matched_extractions.items():
                for p in predictions:
                    if p.alignment_status != lxdata.AlignmentStatus.MATCH_FUZZY:
                        continue
                        
                    fuzzy_text = p.extraction_text
                    org_text    = document.text[p.char_interval.start_pos:p.char_interval.end_pos]

                    pred_tokens = [token.text.lower() for token in nlp.make_doc(fuzzy_text.strip())]
                    gold_tokens = [token.text.lower() for token in nlp.make_doc(org_text.strip())]
                    rows.append({
                        "file" : document.document_id,
                        "true" : org_text,
                        "pred" : fuzzy_text,
                        "diff" : Counter(gold_tokens) - Counter(pred_tokens)
                    })
        return rows 
    
    
    
    def evaluate_items(self):
        rows = []
        for document in self.documents:
            subspan = superspan = exact = partial = missed = hits = disjoint = duplicate_fp = iou = token_r = token_p = 0 
            fuzzy = smaller = 0
            multimatch = False
            iou = avg(
                [max(
                    (
                        intersection_over_union(document.gt_extractions[t_index].char_interval,p.char_interval)
                        for p in predictions
                    )
                    ,default=0)
                for t_index,predictions in document.matched_extractions.items() if t_index != None]
            ) 
            for t_index,predictions in document.matched_extractions.items():
                fuzzy += sum(1 for p in predictions if p.alignment_status == lxdata.AlignmentStatus.MATCH_FUZZY)
                smaller += sum(1 for p in predictions if p.alignment_status == lxdata.AlignmentStatus.MATCH_LESSER)
                if t_index is None:
                    disjoint += len(predictions)
                    continue
                    
                if len(predictions) == 0:
                    missed +=1
                    continue
                else:
                    hits += 1
                    score = compute_token_score(predictions[0].extraction_text,document.gt_extractions[t_index].extraction_text)
                    token_p += score["token_p"]
                    token_r += score["token_r"]
                    duplicate_fp += max(0, len(predictions) - 1)

                multimatch = multimatch or any(extraction.attributes.get("counter",0) > 1 for extraction in predictions)
                t = document.gt_extractions[t_index].char_interval

                for p in predictions:
                    p = p.char_interval
                    # exact > {subspan,superspan} > overlap
                    if is_exact(t, p):
                        exact += 1
                    elif is_subspan(t, p):
                        subspan += 1
                    elif is_superspan(t, p):
                        superspan += 1
                    elif overlaps(t, p):
                        partial += 1
                    else:
                        raise ValueError("Should not happens")
                    
            rows.append([
                document.document_id,
                len(document.gt_extractions),
                len(document.extractions),
                multimatch,
                len(document.text.split(" ")),
                fuzzy, smaller,
                subspan,superspan,exact,partial,disjoint,duplicate_fp,disjoint + duplicate_fp,missed,hits,iou,pd.NA if hits == 0 else token_p/hits,pd.NA if hits == 0 else token_r/hits
            ])
        df = pd.DataFrame(rows,columns=[
            "File","Reference","Prediction","MultiMatch","Size","Fuzzy","Smaller","Subspan","Superspan","Exact","Partial","Disjoint (FP)","Duplicate Match (FP)","FP","FN","TP","IoU","token_p","token_r"
            ])
        return df
            
    def false_positives(self):
        rows = []
        for document in self.documents: 
            if None not in document.matched_extractions:             
                continue
            for extraction in document.matched_extractions[None]:
                rows.append((document.document_id,extraction))
        return rows 
    
    def false_negatives(self):
        rows = []
        for document in self.documents: 
            for gt,p in document.matched_extractions.items():             
                if gt is None: continue
                if len(p) != 0: continue
                rows.append((document.document_id,document.gt_extractions[gt]))
        return rows 
    
    def evaluate_metrics(self):
        df = self.evaluate_items()

        tp = float(df["TP"].sum())
        fp = float(df["FP"].sum())
        fn = float(df["FN"].sum()) 
        fuzzy = (df["Fuzzy"].sum() + df["Smaller"].sum())  / df["Prediction"].sum()

        precision = tp / (tp + fp + 1e-9)
        recall = tp / (tp + fn + 1e-9)
        f1 = 2 * precision * recall / (precision + recall + 1e-9)

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "fuzzy_rate" : fuzzy,
            "smaller" : df["Smaller"].sum(),
            "fuzzy"  : df["Fuzzy"].sum(),
            "token_p" : float((df["token_p"].fillna(0) * df["TP"]).sum() / (df["TP"].sum() + 1e-9)),
            "token_r" : float((df["token_r"].fillna(0) * df["TP"]).sum() / (df["TP"].sum() + 1e-9))
        }
    
    def export_annotations(self):
        # reannotate documents with GT tags
        newDocuments = []
        for document in self.documents:
            extractions = []
            
            reference = copy.deepcopy(document.gt_extractions)
            for extraction in reference:
                extractions.append(
                    {
                        "extraction_class" : "reference",
                        "extraction_text" : extraction.extraction_text,
                        "char_interval": {"start_pos": extraction.char_interval.start_pos, "end_pos": extraction.char_interval.end_pos},
                        "alignment_status" : lxdata.AlignmentStatus.MATCH_EXACT
                    }
                )
                
            prediction = copy.deepcopy(document.extractions)
            for extraction in prediction:
                extractions.append(
                    {
                        "extraction_class" : "prediction",
                        "extraction_text" : extraction.extraction_text,
                        "char_interval": {"start_pos": extraction.char_interval.start_pos, "end_pos": extraction.char_interval.end_pos},
                        "attributes" : {
                            "alignment" : extraction.alignment_status.value,
                            "start" : extraction.char_interval.start_pos,
                            "end" : extraction.char_interval.end_pos,
                        } 
                    }
                )
            extractions.sort(key=lambda x:(x["char_interval"]["start_pos"],x["char_interval"]["end_pos"]))
            data = {
                "text": document.text,
                "document_id" : document.document_id,
                "extractions": extractions
            }
            
            newDocuments.append(
                lx.data_lib.dict_to_annotated_document(data)
            )
        
        lx.io.save_annotated_documents(newDocuments,self.experiment_path / "outputs",f"analysis-{self.stage}.jsonl",show_progress = False)
        
    @classmethod
    def results_to_yaml(cls,path : Path|str,keepFuzzy : bool = False):
        path = Path(path)
        if not path.exists() or path.suffix != ".jsonl":
            raise ValueError(f"Wrong Path {path}")
        annotated_docs = lx.io.load_annotated_documents_jsonl(path,show_progress = False)
        
        data = defaultdict(list)
        for document in annotated_docs:
            file = document.document_id
            for extraction in document.extractions:
                if not keepFuzzy and extraction.alignment_status != lxdata.AlignmentStatus.MATCH_EXACT:
                    continue
                data[file].append(
                    {
                        "extraction_class" : "security_advice",
                        "extraction_text": extraction.extraction_text,
                        "attributes" : {}
                    }
                )
        def indent_block(text: str, spaces: int = 6):
            prefix = " " * spaces
            lines = text.splitlines()
            return "\n".join(prefix + line if line.strip() else prefix for line in lines)

        with (path.parent / f"{path.stem}.yaml").open("w") as f:
            for file, extractions in data.items():
                f.write(f'"{file}":\n')
                
                if not extractions:                
                    f.write("  extractions: []\n")
                    continue

                f.write("  extractions: \n")
                for e in extractions:
                    f.write(f'  - extraction_class: "{e["extraction_class"]}"\n')
                    f.write("    extraction_text: |\n")
                    f.write(indent_block(e["extraction_text"]) + "\n")
                    if e["attributes"]:
                        f.write("    attributes:\n")
                        f.write(f'      type: "{e["attributes"]["type"]}"\n')
                    else:
                        f.write("    attributes: {}\n")