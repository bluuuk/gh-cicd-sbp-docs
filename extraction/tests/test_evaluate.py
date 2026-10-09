import importlib.util
import enum
import sys
import types
import unittest
import uuid
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


EVALUATE_PATH = Path(__file__).resolve().parents[1] / "evaluate.py"


def resolve_langextract_root():
    candidates = [
        Path("/workspace/langextract/langextract"),
        Path(__file__).resolve().parents[2] / "langextract" / "langextract",
    ]
    for candidate in candidates:
        if (candidate / "core" / "data.py").exists():
            return candidate
    raise FileNotFoundError("Could not locate langextract source tree")


LANGEXTRACT_ROOT = resolve_langextract_root()


def load_module_from_path(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_langextract_modules():
    class FormatType(enum.Enum):
        YAML = "yaml"
        JSON = "json"

    @dataclass
    class TokenInterval:
        start_index: int = 0
        end_index: int = 0

    @dataclass
    class TokenizedText:
        text: str
        tokens: list = None

        def __post_init__(self):
            if self.tokens is None:
                self.tokens = []

    tokenizer_module = types.ModuleType("langextract.core.tokenizer")
    tokenizer_module.TokenInterval = TokenInterval
    tokenizer_module.TokenizedText = TokenizedText
    tokenizer_module.tokenize = lambda text: TokenizedText(text=text, tokens=[])

    types_module = types.ModuleType("langextract.core.types")
    types_module.FormatType = FormatType

    langextract_module = types.ModuleType("langextract")
    langextract_module.__path__ = []

    core_module = types.ModuleType("langextract.core")
    core_module.__path__ = []

    sys.modules["langextract"] = langextract_module
    sys.modules["langextract.core"] = core_module
    sys.modules["langextract.core.tokenizer"] = tokenizer_module
    sys.modules["langextract.core.types"] = types_module

    data_module = load_module_from_path(
        "langextract.core.data",
        LANGEXTRACT_ROOT / "core" / "data.py",
    )
    data_lib_module = load_module_from_path(
        "langextract.data_lib",
        LANGEXTRACT_ROOT / "data_lib.py",
    )

    core_module.tokenizer = tokenizer_module
    core_module.types = types_module
    core_module.data = data_module
    langextract_module.core = core_module
    langextract_module.data_lib = data_lib_module

    return langextract_module, data_module, data_lib_module


def load_evaluate_module(*, annotated_docs=None, yaml_data=None):
    annotated_docs = [] if annotated_docs is None else annotated_docs
    yaml_data = {} if yaml_data is None else yaml_data
    state = {
        "loaded_paths": [],
        "saved_calls": [],
        "yaml_stream_names": [],
    }

    def load_annotated_documents_jsonl(path, show_progress=True):
        state["loaded_paths"].append(Path(path))
        return list(annotated_docs)

    def save_annotated_documents(
        annotated_documents,
        output_dir=None,
        output_name="data.jsonl",
        show_progress=True,
    ):
        state["saved_calls"].append(
            {
                "documents": list(annotated_documents),
                "output_dir": output_dir,
                "output_name": output_name,
                "show_progress": show_progress,
            }
        )

    class FakeSeries(list):
        def sum(self):
            return sum(self)

    class FakeDataFrame:
        def __init__(self, rows, columns):
            self._rows = rows
            self.columns = columns

        def __getitem__(self, key):
            index = self.columns.index(key)
            return FakeSeries(row[index] for row in self._rows)

    langextract_module, data_module, data_lib_module = load_langextract_modules()

    langextract_module.io = types.SimpleNamespace(
        load_annotated_documents_jsonl=load_annotated_documents_jsonl,
        save_annotated_documents=save_annotated_documents,
    )
    langextract_module.data_lib = data_lib_module

    pandas_module = types.ModuleType("pandas")
    pandas_module.DataFrame = FakeDataFrame

    def safe_load(stream):
        state["yaml_stream_names"].append(getattr(stream, "name", None))
        return yaml_data

    yaml_module = types.ModuleType("yaml")
    yaml_module.safe_load = safe_load

    utils_module = types.ModuleType("utils")

    sys.modules["langextract"] = langextract_module
    sys.modules["pandas"] = pandas_module
    sys.modules["yaml"] = yaml_module
    sys.modules["utils"] = utils_module

    module_name = f"_qa_evaluate_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, EVALUATE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)

    state["classes"] = types.SimpleNamespace(
        CharInterval=data_module.CharInterval,
        Extraction=data_module.Extraction,
        AnnotatedDocument=data_module.AnnotatedDocument,
        AlignmentStatus=data_module.AlignmentStatus,
    )
    return module, state


def row_as_dict(df, row_index=0):
    return dict(zip(df.columns, df._rows[row_index]))


def build_comprehensive_fixture(spans):
    text = (
        "exact_anchor | "
        "broad_superspan_zone | "
        "xxnarrow_subspanyy | "
        "partialABCDEtail | "
        "bridge_left bridge_right | "
        "EDGETOUCH | "
        "duplicate_anchor | "
        "far_anchor"
    )

    def char_interval(snippet):
        start = text.index(snippet)
        return spans.CharInterval(start, start + len(snippet))

    def prediction(extraction_class, snippet):
        return spans.Extraction(
            extraction_class=extraction_class,
            extraction_text=snippet,
            char_interval=char_interval(snippet),
            attributes={"type": "textual"},
        )

    annotated_doc = spans.AnnotatedDocument(
        text=text,
        document_id="interactions.md",
        extractions=[
            prediction("exact", "exact_anchor"),
            prediction("prediction_inside_gt", "superspan"),
            prediction("gt_inside_prediction", "xxnarrow_subspanyy"),
            prediction("partial_overlap", "ABCDEtail"),
            prediction("bridge_both_gt", "bridge_left bridge_right"),
            prediction("touching_only", "EDGE"),
            prediction("duplicate_prediction", "duplicate_anchor"),
            prediction("duplicate_prediction", "duplicate_anchor"),
            prediction("disjoint_prediction", "far_anchor"),
        ],
    )

    yaml_data = {
        "interactions.md": {
            "extractions": [
                {
                    "extraction_class": "exact",
                    "extraction_text": "exact_anchor",
                    "attributes": {"type": "textual"},
                },
                {
                    "extraction_class": "prediction_inside_gt",
                    "extraction_text": "broad_superspan_zone",
                    "attributes": {"type": "textual"},
                },
                {
                    "extraction_class": "gt_inside_prediction",
                    "extraction_text": "narrow_subspan",
                    "attributes": {"type": "textual"},
                },
                {
                    "extraction_class": "partial_overlap",
                    "extraction_text": "partialABCDE",
                    "attributes": {"type": "textual"},
                },
                {
                    "extraction_class": "bridge_left",
                    "extraction_text": "bridge_left",
                    "attributes": {"type": "textual"},
                },
                {
                    "extraction_class": "bridge_right",
                    "extraction_text": "bridge_right",
                    "attributes": {"type": "textual"},
                },
                {
                    "extraction_class": "touching_only",
                    "extraction_text": "TOUCH",
                    "attributes": {"type": "textual"},
                },
                {
                    "extraction_class": "duplicate_prediction",
                    "extraction_text": "duplicate_anchor",
                    "attributes": {"type": "textual"},
                },
            ]
        }
    }
    return annotated_doc, yaml_data


class EvaluateTests(unittest.TestCase):
    def build_evaluator(self, *, stage="test", path_as_string=False):
        module, state = load_evaluate_module()
        spans = state["classes"]
        annotated_doc, yaml_data = build_comprehensive_fixture(spans)
        module, state = load_evaluate_module(
            annotated_docs=[annotated_doc],
            yaml_data=yaml_data,
        )

        with TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            (base / "outputs").mkdir()
            (base / "outputs" / f"result-{stage}.jsonl").write_text("", encoding="utf-8")
            (base / f"{stage}.yaml").write_text("ignored", encoding="utf-8")
            evaluator = module.Evaluator(str(base) if path_as_string else base, stage=stage)
        return module, state, evaluator

    def test_comprehensive_interactions_are_bucketed_correctly(self):
        module, state = load_evaluate_module()
        spans = state["classes"]
        annotated_doc, yaml_data = build_comprehensive_fixture(spans)
        gt_extractions = [
            spans.Extraction(**args)
            for args in yaml_data["interactions.md"]["extractions"]
        ]

        evaluated = module.EvaluatedDocument.from_annotated(annotated_doc, gt_extractions)

        self.assertEqual(
            [item.extraction_class for item in evaluated.matched_extractions[0]],
            ["exact"],
        )
        self.assertEqual(
            [item.extraction_class for item in evaluated.matched_extractions[1]],
            ["prediction_inside_gt"],
        )
        self.assertEqual(
            [item.extraction_class for item in evaluated.matched_extractions[2]],
            ["gt_inside_prediction"],
        )
        self.assertEqual(
            [item.extraction_class for item in evaluated.matched_extractions[3]],
            ["partial_overlap"],
        )
        self.assertEqual(
            [item.extraction_class for item in evaluated.matched_extractions[4]],
            ["bridge_both_gt"],
        )
        self.assertEqual(
            [item.extraction_class for item in evaluated.matched_extractions[5]],
            ["bridge_both_gt"],
        )
        self.assertEqual(evaluated.matched_extractions[6], [])
        self.assertEqual(
            [item.extraction_class for item in evaluated.matched_extractions[7]],
            ["duplicate_prediction", "duplicate_prediction"],
        )
        self.assertEqual(
            [item.extraction_class for item in evaluated.matched_extractions[None]],
            ["touching_only", "disjoint_prediction"],
        )

    def test_comprehensive_interactions_drive_current_metrics(self):
        _, _, evaluator = self.build_evaluator()

        row = row_as_dict(evaluator.evaluate_items())
        metrics = evaluator.evaluate_metrics()

        self.assertEqual(row["Reference"], 8)
        self.assertEqual(row["Prediction"], 9)
        self.assertEqual(row["Subspan"], 3)
        self.assertEqual(row["Superspan"], 1)
        self.assertEqual(row["Exact"], 3)
        self.assertEqual(row["Partial"], 1)
        self.assertEqual(row["Disjoint (FP)"], 2)
        self.assertEqual(row["Duplicate Match (FP)"], 1)
        self.assertEqual(row["FP"], 3)
        self.assertEqual(row["FN"], 1)
        self.assertEqual(row["TP"], 7)

        self.assertAlmostEqual(metrics["tp"], 7.0)
        self.assertAlmostEqual(metrics["fp"], 3.0)
        self.assertAlmostEqual(metrics["fn"], 1.0)
        self.assertAlmostEqual(metrics["precision"], 0.7, places=6)
        self.assertAlmostEqual(metrics["recall"], 0.875, places=6)

    def test_comprehensive_interactions_drive_alternative_metrics(self):
        _, _, evaluator = self.build_evaluator()

        row = row_as_dict(evaluator.evaluate_items_alternative())

        self.assertEqual(row["Reference"], 8)
        self.assertEqual(row["Prediction"], 9)
        self.assertEqual(row["Subspan"], 2)
        self.assertEqual(row["Superspan"], 1)
        self.assertEqual(row["Exact"], 2)
        self.assertEqual(row["Partial"], 1)
        self.assertEqual(row["FP"], 3)
        self.assertEqual(row["FN"], 2)
        self.assertEqual(row["TP"], 6)

    def test_evaluator_accepts_string_paths_and_stage_specific_files(self):
        _, state, evaluator = self.build_evaluator(stage="validation", path_as_string=True)

        self.assertIsInstance(evaluator.experiment_path, Path)
        self.assertEqual(state["loaded_paths"][0].name, "result-validation.jsonl")
        self.assertEqual(
            Path(state["yaml_stream_names"][0]).name,
            "validation.yaml",
        )


if __name__ == "__main__":
    unittest.main()
