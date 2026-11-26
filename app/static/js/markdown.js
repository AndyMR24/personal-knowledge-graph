const SAFE_PROTOCOLS = new Set(["http:", "https:", "mailto:"]);

function appendText(parent, text) {
    if (text) {
        parent.append(document.createTextNode(text));
    }
}

function safeHref(rawUrl) {
    const value = rawUrl.trim().replace(/^<|>$/g, "");
    if (!value) {
        return null;
    }

    try {
        const parsed = new URL(value, window.location.href);
        return SAFE_PROTOCOLS.has(parsed.protocol) ? parsed.href : null;
    } catch {
        return null;
    }
}

function appendInline(parent, source) {
    let index = 0;
    let textBuffer = "";

    const flushText = () => {
        appendText(parent, textBuffer);
        textBuffer = "";
    };

    while (index < source.length) {
        const remaining = source.slice(index);

        if (source[index] === "`") {
            const closing = source.indexOf("`", index + 1);
            if (closing > index + 1) {
                flushText();
                const code = document.createElement("code");
                code.textContent = source.slice(index + 1, closing);
                parent.append(code);
                index = closing + 1;
                continue;
            }
        }

        if (remaining.startsWith("**")) {
            const closing = source.indexOf("**", index + 2);
            if (closing > index + 2) {
                flushText();
                const strong = document.createElement("strong");
                appendInline(strong, source.slice(index + 2, closing));
                parent.append(strong);
                index = closing + 2;
                continue;
            }
        }

        if (source[index] === "*" && source[index + 1] !== "*") {
            const closing = source.indexOf("*", index + 1);
            if (closing > index + 1) {
                flushText();
                const emphasis = document.createElement("em");
                appendInline(emphasis, source.slice(index + 1, closing));
                parent.append(emphasis);
                index = closing + 1;
                continue;
            }
        }

        if (source[index] === "[") {
            const labelEnd = source.indexOf("](", index + 1);
            const urlEnd = labelEnd >= 0 ? source.indexOf(")", labelEnd + 2) : -1;
            if (labelEnd > index + 1 && urlEnd > labelEnd + 2) {
                const label = source.slice(index + 1, labelEnd);
                const href = safeHref(source.slice(labelEnd + 2, urlEnd));
                if (href) {
                    flushText();
                    const link = document.createElement("a");
                    link.href = href;
                    link.target = "_blank";
                    link.rel = "noopener noreferrer";
                    appendInline(link, label);
                    parent.append(link);
                    index = urlEnd + 1;
                    continue;
                }
            }
        }

        textBuffer += source[index];
        index += 1;
    }

    flushText();
}

function startsBlock(line) {
    return (
        /^```/.test(line)
        || /^#{1,3}\s+/.test(line)
        || /^>\s?/.test(line)
        || /^[-*+]\s+/.test(line)
        || /^\d+\.\s+/.test(line)
        || /^---+$/.test(line)
    );
}

function createParagraph(lines) {
    const paragraph = document.createElement("p");
    appendInline(paragraph, lines.join(" ").trim());
    return paragraph;
}

export function renderMarkdown(source) {
    const root = document.createElement("div");
    root.className = "markdown-body";

    if (!source) {
        root.append(createParagraph(["No notes recorded yet."]));
        return root;
    }

    const lines = String(source).replace(/\r\n?/g, "\n").split("\n");
    let index = 0;

    while (index < lines.length) {
        const line = lines[index];

        if (!line.trim()) {
            index += 1;
            continue;
        }

        const fence = line.match(/^```([A-Za-z0-9_-]*)\s*$/);
        if (fence) {
            const codeLines = [];
            index += 1;
            while (index < lines.length && !/^```\s*$/.test(lines[index])) {
                codeLines.push(lines[index]);
                index += 1;
            }
            if (index < lines.length) {
                index += 1;
            }

            const pre = document.createElement("pre");
            const code = document.createElement("code");
            if (fence[1]) {
                code.className = `language-${fence[1]}`;
            }
            code.textContent = codeLines.join("\n");
            pre.append(code);
            root.append(pre);
            continue;
        }

        const heading = line.match(/^(#{1,3})\s+(.+)$/);
        if (heading) {
            const headingElement = document.createElement(`h${heading[1].length + 1}`);
            appendInline(headingElement, heading[2]);
            root.append(headingElement);
            index += 1;
            continue;
        }

        if (/^---+$/.test(line.trim())) {
            root.append(document.createElement("hr"));
            index += 1;
            continue;
        }

        if (/^>\s?/.test(line)) {
            const quoteLines = [];
            while (index < lines.length && (/^>\s?/.test(lines[index]) || !lines[index].trim())) {
                if (lines[index].trim()) {
                    quoteLines.push(lines[index].replace(/^>\s?/, ""));
                }
                index += 1;
            }
            const quote = document.createElement("blockquote");
            quote.append(createParagraph(quoteLines));
            root.append(quote);
            continue;
        }

        if (/^[-*+]\s+/.test(line)) {
            const list = document.createElement("ul");
            while (index < lines.length && /^[-*+]\s+/.test(lines[index])) {
                const item = document.createElement("li");
                appendInline(item, lines[index].replace(/^[-*+]\s+/, ""));
                list.append(item);
                index += 1;
            }
            root.append(list);
            continue;
        }

        if (/^\d+\.\s+/.test(line)) {
            const list = document.createElement("ol");
            while (index < lines.length && /^\d+\.\s+/.test(lines[index])) {
                const item = document.createElement("li");
                appendInline(item, lines[index].replace(/^\d+\.\s+/, ""));
                list.append(item);
                index += 1;
            }
            root.append(list);
            continue;
        }

        const paragraphLines = [line.trim()];
        index += 1;
        while (
            index < lines.length
            && lines[index].trim()
            && !startsBlock(lines[index])
        ) {
            paragraphLines.push(lines[index].trim());
            index += 1;
        }
        root.append(createParagraph(paragraphLines));
    }

    return root;
}
