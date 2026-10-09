import { remark } from "remark";
import { visit, CONTINUE } from "unist-util-visit";
import remarkGfm from "remark-gfm";
import { isConstructorDeclaration } from "typescript";

var counter = 0;

function removeCode() {
    return (tree: any) => {
        visit(tree, "code", (node: any, index: number | undefined, parent: any) => {
            if (![null, "text"].includes(node.lang)) {
                node.value = `[REDACTED@${counter}]`
                counter += 1;
            }
        });
    };
}

function removeHTML() {
    return (tree: any) => {
        visit(tree, "html", (node: any, index: number | undefined, parent: any) => {
            if (node.value.startsWith("<!--")) {
                parent.children.splice(index, 1);
                return [CONTINUE, index];
            }
            if (/^<\/?(svg|path)\b/i.test(node.value)) {
                parent.children.splice(index, 1);
                return [CONTINUE, index];
            }
        });
    };
}

async function cleanMarkdown(input: Input): Promise<string> {
    const parsed = await remark()
        .use(remarkGfm)
        .use(removeCode)
        .use(removeHTML)
        .process(input.body);
    
    /*
        remove &#x20; (HTML Code for whitespace) happening due to `removeHTML`
        remove leading tabs and whitespaces
    */
    return String(parsed).replace(/&#x20;/g, " ").replace(/^[ \t]+/gm, ""); 
}

type Input = {
  body: string;
};

if (Bun.argv.length === 3) {
    const path = Bun.argv[2];
    if (!path) {
        process.exit(1);
    }

    const file = Bun.file(path);
    const data = await file.json();
    
    console.log(await cleanMarkdown(data));
}