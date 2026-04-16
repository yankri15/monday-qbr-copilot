import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";

const ROOT = "/Users/yankri/Documents/Monday";
const require = createRequire(path.join(ROOT, "frontend/package.json"));
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const ReactMarkdown = require("react-markdown").default;
const remarkGfm = require("remark-gfm").default;

const docs = [
  {
    input: path.join(ROOT, "docs/design_brief.md"),
    output: path.join(ROOT, "tmp/pdfs/design_brief.html"),
    title: "QBR Co-Pilot Design Brief",
  },
  {
    input: path.join(ROOT, "docs/backend_architecture.md"),
    output: path.join(ROOT, "tmp/pdfs/flow_architecture_diagram.html"),
    title: "QBR Co-Pilot Flow Architecture Diagram",
  },
  {
    input: path.join(ROOT, "docs/prompts_documentation.md"),
    output: path.join(ROOT, "tmp/pdfs/prompts_components_documentation.html"),
    title: "QBR Co-Pilot Prompts and Components Documentation",
  },
];

const styles = `
  :root {
    --text: #1f2937;
    --muted: #5b6473;
    --line: #d7dbe3;
    --accent: #334155;
    --code-bg: #f5f6f8;
    --table-head: #f3f4f6;
  }

  * { box-sizing: border-box; }

  @page {
    size: A4;
    margin: 22mm 18mm 22mm 18mm;
  }

  body {
    margin: 0;
    background: white;
    color: var(--text);
    font-family: "Aptos", "Calibri", "Segoe UI", Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.45;
  }

  main {
    max-width: 820px;
    margin: 0 auto;
    padding: 0;
  }

  .sheet {
    padding: 0;
  }

  h1, h2, h3, h4 {
    color: var(--text);
    margin-top: 1.15em;
    margin-bottom: 0.45em;
    line-height: 1.25;
    break-after: avoid-page;
    page-break-after: avoid;
  }

  h1 {
    margin-top: 0;
    font-size: 20pt;
    font-weight: 700;
  }

  h2 {
    font-size: 14pt;
    font-weight: 700;
  }

  h3 {
    font-size: 12pt;
    font-weight: 700;
  }

  p, li {
    font-size: 11pt;
  }

  p, ul, ol, table, pre, blockquote {
    margin-top: 0;
    margin-bottom: 0.85em;
  }

  ul, ol {
    padding-left: 1.4em;
  }

  li + li {
    margin-top: 0.2em;
  }

  a {
    color: inherit;
    text-decoration: none;
  }

  code {
    font-family: "SFMono-Regular", Menlo, Consolas, monospace;
    background: var(--code-bg);
    padding: 0.08em 0.28em;
    border-radius: 4px;
    font-size: 0.95em;
  }

  pre {
    background: #fbfbfc;
    color: var(--text);
    border: 1px solid var(--line);
    padding: 10px 12px;
    border-radius: 0;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: anywhere;
  }

  pre code {
    background: transparent;
    color: inherit;
    padding: 0;
  }

  .mermaid-wrap {
    margin: 0.8em 0 1em;
    border: 1px solid var(--line);
    padding: 10px 12px;
    page-break-inside: avoid;
    break-inside: avoid;
  }

  .mermaid {
    display: flex;
    justify-content: center;
  }

  .mermaid svg {
    max-width: 100%;
    height: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10.5pt;
    margin-bottom: 1em;
    page-break-inside: avoid;
    break-inside: avoid;
  }

  th, td {
    border: 1px solid var(--line);
    padding: 7px 9px;
    text-align: left;
    vertical-align: top;
  }

  th {
    background: var(--table-head);
    font-weight: 700;
  }

  blockquote {
    margin-left: 0;
    padding: 8px 12px;
    border-left: 3px solid #b8c0cc;
    background: #fafafa;
    color: var(--muted);
  }

  hr {
    display: none;
  }

  strong {
    font-weight: 700;
  }

  .md-root > h1:first-child {
    margin-top: 0;
  }

  .md-root p,
  .md-root li {
    widows: 3;
    orphans: 3;
  }

  @media print {
    main {
      max-width: none;
      margin: 0;
      padding: 0;
    }

    .sheet {
      padding: 0;
    }
  }
`;

function MarkdownDocument({ title, markdown }) {
  const components = {
    code(props) {
      const { className, children, node, ...rest } = props;
      const content = String(children ?? "");

      const isInline = !className && !content.includes("\n");
      if (isInline) {
        return React.createElement("code", rest, content.trim());
      }
      return React.createElement("code", { className, ...rest }, content.trimEnd());
    },
    pre(props) {
      const child = props.children;
      if (React.isValidElement(child)) {
        const className = child.props.className ?? "";
        const content = String(child.props.children ?? "").trim();
        if (className.includes("language-mermaid")) {
          return React.createElement(
            "div",
            { className: "mermaid-wrap" },
            React.createElement("div", { className: "mermaid" }, content),
          );
        }
      }
      return React.createElement("pre", null, props.children);
    },
  };

  return React.createElement(
    "html",
    { lang: "en" },
    React.createElement(
      "head",
      null,
      React.createElement("meta", { charSet: "utf-8" }),
      React.createElement("meta", {
        name: "viewport",
        content: "width=device-width, initial-scale=1",
      }),
      React.createElement("title", null, title),
      React.createElement("style", null, styles),
      React.createElement("script", {
        type: "module",
        dangerouslySetInnerHTML: {
          __html: `
            import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
            mermaid.initialize({
              startOnLoad: false,
              theme: "neutral",
              securityLevel: "loose",
              flowchart: { useMaxWidth: true, htmlLabels: true }
            });

            window.addEventListener("load", async () => {
              const nodes = document.querySelectorAll(".mermaid");
              if (nodes.length > 0) {
                await mermaid.run({ nodes });
              }
              window.__PDF_READY__ = true;
            });
          `,
        },
      }),
    ),
    React.createElement(
      "body",
      null,
      React.createElement(
        "main",
        null,
        React.createElement(
          "section",
          { className: "sheet" },
          React.createElement(ReactMarkdown, {
            remarkPlugins: [remarkGfm],
            components,
            className: "md-root",
            children: markdown,
          }),
        ),
      ),
    ),
  );
}

for (const doc of docs) {
  const markdown = await fs.readFile(doc.input, "utf8");
  const html = "<!DOCTYPE html>\n" + renderToStaticMarkup(
    React.createElement(MarkdownDocument, {
      title: doc.title,
      markdown,
    }),
  );
  await fs.writeFile(doc.output, html, "utf8");
  console.log(`Wrote ${doc.output}`);
}
