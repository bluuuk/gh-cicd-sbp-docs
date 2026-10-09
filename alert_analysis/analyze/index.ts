import { Glob } from "bun";
import { toMarkdown } from "mdast-util-to-markdown";
import path from "node:path";
import { remark } from "remark";
import remarkFrontmatter from "remark-frontmatter";
import remarkGfm from "remark-gfm";
import remarkParse from "remark-parse";
import { visit } from "unist-util-visit";

const debug =  process.env["DEBUG"] || false

enum HighlightType {
    caution = "caution",
    important = "important",
    note = "note",
    tip = "tip",
    warning = "warning",
    unknown = "unknown"
}

interface Highlight {
    type: HighlightType
    content: string
}

interface FileHighlight {
    file : string
    words: Number
    highlight : Array<Highlight>
}

/*
Some null byte shit:
    ❯ bun run index.ts "../../docs/content"
    [ "/opt/homebrew/Cellar/bun/1.3.6/bin/bun", "/Users/bluk/Developer/github-best-pratices/analysis/index.ts",
    "../../docs/content"
    ]
    ENOENT: no such file or directory, open '../../docs/conten'
        path: "../../docs/conten\u0000",
    syscall: "open",
    errno: -2,
        code: "ENOENT"
*/


const basePath = path.resolve(process.cwd(), process.argv[2] ?? "../docs/content");
console.log("Using basepath of " + basePath)
// change to md for the processed ones
// const globber = new Glob("**/*.{json}");
const globber = new Glob("**/*.{md}");

let scanned = 0 
let found = 0

function countWords(text : string) {
  const segmenter = new Intl.Segmenter("en", { granularity: "word" });
  return [...segmenter.segment(text)]
    .filter(s => s.isWordLike)
    .length;
}


type Input = {
  body: string;
};

const highlights = new Array<FileHighlight>()
for await (const relativePath of globber.scan({ cwd: basePath })) {
    if(relativePath.indexOf("README.json") > 0 || relativePath.indexOf("index.json") > 0)continue
    scanned += 1
    const file = path.join(basePath, relativePath);
    // const content = (await Bun.file(file).json()).body
    // change to .text() for processed one for markdown
    const content = (await Bun.file(file).text())
    const parsed = await parseUnifiedRemark(file,content)
    found += parsed.length
    highlights.push({
        file : file,
        words : countWords(content),
        highlight: parsed
    })
}

console.log(`Scanned ${scanned} files and found ${found}`)

if(!debug){
    Bun.write(
        Bun.file(
            path.join(process.cwd(),"analyzed.json")
        ),
        JSON.stringify(highlights)   
    )
}

async function parseUnifiedRemark(file : string,input : string) : Promise<Array<Highlight>>{
    const highlights = new Array<Highlight>()
    const tree = await remark().use(remarkParse).use(remarkFrontmatter).use(remarkGfm).parse(input)
    visit(tree, "blockquote", (node) => {
        const paragraphHeader = node.children[0] 
        if (paragraphHeader?.type !== "paragraph") return
        
        const header = paragraphHeader.children[0]
        if (header?.type !== "text") return
        const match = header.value.match(/\[!(\w+)\]/);
        if(!match || !match[1]) return

        // easiest way to remove the alert type marker
        let markdown = toMarkdown(node)
        markdown = markdown.substring(markdown.indexOf("]") + 1).split("\n").map(line => line.replace(/^\s*>\s?/, "")).join("\n").trim()
        highlights.push({
            type: (match[1].toLowerCase() ?? HighlightType.unknown) as HighlightType,
            content: markdown,
        });
    });
    return highlights
}

// // @ts-ignore
// import markdownit from 'markdown-it'
// // @ts-ignore
// import ParserBlock from 'markdown-it'
// const md = markdownit('commonmark')
// function parseMarkdownit(file : string,input : string) {
//     const outTokens = new Array<any>
//     const tokens = new ParserBlock(input,md,{},outTokens)
//     for (const token of tokens){
//         log(token)
//         if (token.tag !== "blockquote")continue
//     }
// }

//// // @ts-ignore
// import { Parser } from 'commonmark';
// function parseCommon(file : string,input : string) {
//     var reader = new Parser({smart: true}).parse(input);
//     var walker = reader.walker();
//     var event, node;

//     while ((event = walker.next())) {
//         node = event.node;
//         if (event.entering && node.type === 'block_quote') {
//             log(node.literal)
//         }
//     }
// }


// async function parseMarked(file : string,input : string) {
//     const tokens = await marked.lexer(input);

//     for (const token of tokens) {
//         console.log(token)
//         if (token.type !== "blockquote") continue;

//         const text : string = token.text;
//         const match = text.match(/^\[!(\w+)\]/);
//         if (!match) continue;

//         found +=1
        
//         highlights.push({
//             file,
//             type: (match[1]?.toLowerCase() ?? HighlightType.unknown) as HighlightType,
//             content: text.replace(/\[![^\]]+\]\s*/i, "").trim()
//         });
//     }
// }