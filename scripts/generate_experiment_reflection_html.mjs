import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";

const ROOT = "/Users/yankri/Documents/Monday";
const require = createRequire(path.join(ROOT, "frontend/package.json"));
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const ReactMarkdown = require("react-markdown").default;
const remarkGfm = require("remark-gfm").default;

const input = path.join(ROOT, "docs/experiment_reflection.md");
const output = path.join(ROOT, "tmp/pdfs/experiment_reflection.html");

const styles = `
  :root {
    --text: #1f2937;
    --muted: #5b6473;
    --line: #d7dbe3;
    --code-bg: #f5f6f8;
  }

  * { box-sizing: border-box; }

  @page {
    size: A4;
    margin: 12mm 12mm 12mm 12mm;
  }

  body {
    margin: 0;
    background: white;
    color: var(--text);
    font-family: "Aptos", "Calibri", "Segoe UI", Arial, sans-serif;
    font-size: 9.8pt;
    line-height: 1.26;
  }

  main {
    max-width: 820px;
    margin: 0 auto;
    padding: 0;
  }

  h1, h2, h3, h4 {
    color: var(--text);
    line-height: 1.24;
    break-after: avoid-page;
    page-break-after: avoid;
  }

  h1 {
    margin: 0 0 0.28em 0;
    font-size: 17.2pt;
    font-weight: 700;
  }

  h2 {
    margin: 0.52em 0 0.16em 0;
    font-size: 11.7pt;
    font-weight: 700;
  }

  p, li {
    font-size: 9.8pt;
  }

  p, ul, ol {
    margin-top: 0;
    margin-bottom: 0.3em;
  }

  ul, ol {
    padding-left: 1.25em;
  }

  li + li {
    margin-top: 0.07em;
  }

  strong {
    font-weight: 700;
  }

  code {
    font-family: "SFMono-Regular", Menlo, Consolas, monospace;
    font-size: 0.92em;
    background: var(--code-bg);
    padding: 0.08em 0.28em;
    border-radius: 4px;
  }

  a {
    color: inherit;
    text-decoration: none;
  }

  hr {
    display: none;
  }

  .md-root > h1:first-child {
    margin-top: 0;
  }

  @media print {
    main {
      max-width: none;
      margin: 0;
      padding: 0;
    }
  }
`;

function MarkdownDocument({ markdown }) {
  const components = {
    code(props) {
      const { className, children, ...rest } = props;
      const content = String(children ?? "");
      const isInline = !className && !content.includes("\n");
      if (isInline) {
        return React.createElement("code", rest, content.trim());
      }
      return React.createElement("code", { className, ...rest }, content.trimEnd());
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
      React.createElement("title", null, "QBR Co-Pilot Experiment and Reflection"),
      React.createElement("style", null, styles),
    ),
    React.createElement(
      "body",
      null,
      React.createElement(
        "main",
        null,
        React.createElement(ReactMarkdown, {
          remarkPlugins: [remarkGfm],
          components,
          className: "md-root",
          children: markdown,
        }),
      ),
    ),
  );
}

const markdown = await fs.readFile(input, "utf8");
const html =
  "<!DOCTYPE html>\n" +
  renderToStaticMarkup(React.createElement(MarkdownDocument, { markdown }));
await fs.writeFile(output, html, "utf8");
console.log(`Wrote ${output}`);
