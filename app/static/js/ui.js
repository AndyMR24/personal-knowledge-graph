const modalStack = [];

function modalRoot() {
    return document.getElementById("modal-root");
}

function icon(name) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    if (name === "close") {
        path.setAttribute("d", "m7 7 10 10M17 7 7 17");
    } else {
        path.setAttribute("d", "M5 12h14");
    }
    svg.append(path);
    return svg;
}

function focusableElements(container) {
    return [...container.querySelectorAll(
        'button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), a[href]',
    )].filter(element => !element.closest("[hidden]"));
}

function createCustomSelect(field, value) {
    const root = document.createElement("div");
    root.className = "custom-select";

    const options = field.options || [];
    const valueInput = document.createElement("input");
    valueInput.type = "hidden";
    valueInput.name = field.name;
    valueInput.value = String(value ?? options[0]?.value ?? "");
    valueInput.required = Boolean(field.required);

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "custom-select-trigger";
    trigger.id = `field-${field.name}`;
    trigger.setAttribute("aria-haspopup", "listbox");
    trigger.setAttribute("aria-expanded", "false");
    trigger.setAttribute("aria-required", field.required ? "true" : "false");

    const triggerLabel = document.createElement("span");
    const chevron = document.createElement("span");
    chevron.className = "custom-select-chevron";
    chevron.setAttribute("aria-hidden", "true");
    trigger.append(triggerLabel, chevron);

    const menu = document.createElement("div");
    menu.className = "custom-select-menu";
    menu.setAttribute("role", "listbox");
    menu.hidden = true;

    const optionButtons = options.map(option => {
        const optionButton = document.createElement("button");
        optionButton.type = "button";
        optionButton.className = "custom-select-option";
        optionButton.dataset.value = String(option.value);
        optionButton.setAttribute("role", "option");
        optionButton.textContent = option.label;
        optionButton.addEventListener("click", () => {
            valueInput.value = String(option.value);
            render();
            valueInput.dispatchEvent(new Event("change", { bubbles: true }));
            setOpen(false);
            trigger.focus();
        });
        menu.append(optionButton);
        return optionButton;
    });

    let open = false;
    const selectedOption = () => options.find(
        option => String(option.value) === valueInput.value,
    ) ?? options[0] ?? null;

    const render = () => {
        const current = selectedOption();
        triggerLabel.textContent = current?.label ?? "Select an option";
        for (const optionButton of optionButtons) {
            const isSelected = optionButton.dataset.value === valueInput.value;
            optionButton.classList.toggle("is-selected", isSelected);
            optionButton.setAttribute("aria-selected", isSelected ? "true" : "false");
        }
    };

    const setOpen = nextOpen => {
        open = nextOpen;
        menu.hidden = !open;
        trigger.setAttribute("aria-expanded", open ? "true" : "false");
    };

    const closeOnOutsidePointer = event => {
        if (!document.contains(root)) {
            document.removeEventListener("pointerdown", closeOnOutsidePointer, true);
            return;
        }
        if (!root.contains(event.target)) {
            setOpen(false);
        }
    };
    document.addEventListener("pointerdown", closeOnOutsidePointer, true);

    trigger.addEventListener("click", () => setOpen(!open));
    trigger.addEventListener("keydown", event => {
        if (event.key === "ArrowDown" || event.key === "ArrowUp") {
            event.preventDefault();
            setOpen(true);
            const selected = optionButtons.find(
                option => option.dataset.value === valueInput.value,
            );
            (selected ?? optionButtons[0])?.focus();
        } else if (event.key === "Escape") {
            setOpen(false);
        }
    });

    menu.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            setOpen(false);
            trigger.focus();
            return;
        }
        if (event.key !== "ArrowDown" && event.key !== "ArrowUp") {
            return;
        }
        event.preventDefault();
        const currentIndex = optionButtons.indexOf(document.activeElement);
        const direction = event.key === "ArrowDown" ? 1 : -1;
        const nextIndex = (
            currentIndex + direction + optionButtons.length
        ) % optionButtons.length;
        optionButtons[nextIndex]?.focus();
    });

    render();
    root.append(valueInput, trigger, menu);
    return { root, trigger, valueInput };
}

export function openModal({
    title,
    description = "",
    body,
    size = "normal",
    onClose = null,
    initialFocus = null,
}) {
    const backdrop = document.createElement("div");
    backdrop.className = "modal-backdrop";

    const dialog = document.createElement("section");
    dialog.className = `modal-card modal-${size}`;
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");

    const header = document.createElement("header");
    header.className = "modal-header";

    const heading = document.createElement("div");
    const titleElement = document.createElement("h2");
    titleElement.id = `modal-title-${Date.now()}-${modalStack.length}`;
    titleElement.textContent = title;
    dialog.setAttribute("aria-labelledby", titleElement.id);
    heading.append(titleElement);

    if (description) {
        const descriptionElement = document.createElement("p");
        descriptionElement.textContent = description;
        heading.append(descriptionElement);
    }

    const closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className = "icon-button modal-close";
    closeButton.setAttribute("aria-label", "Close dialog");
    closeButton.append(icon("close"));

    const content = document.createElement("div");
    content.className = "modal-content";
    content.append(body);

    header.append(heading, closeButton);
    dialog.append(header, content);
    backdrop.append(dialog);
    modalRoot().append(backdrop);

    const previousFocus = document.activeElement;
    let closed = false;

    const close = ({ notify = true } = {}) => {
        if (closed) {
            return;
        }
        closed = true;
        const stackIndex = modalStack.findIndex(item => item.backdrop === backdrop);
        if (stackIndex >= 0) {
            modalStack.splice(stackIndex, 1);
        }
        backdrop.remove();
        document.removeEventListener("keydown", handleKeydown);
        if (notify) {
            onClose?.();
        }
        if (previousFocus instanceof HTMLElement && document.contains(previousFocus)) {
            previousFocus.focus();
        }
    };

    const handleKeydown = event => {
        if (modalStack.at(-1)?.backdrop !== backdrop) {
            return;
        }

        if (event.key === "Escape") {
            event.preventDefault();
            close();
            return;
        }

        if (event.key !== "Tab") {
            return;
        }

        const elements = focusableElements(dialog);
        if (elements.length === 0) {
            event.preventDefault();
            dialog.focus();
            return;
        }

        const first = elements[0];
        const last = elements.at(-1);
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    };

    closeButton.addEventListener("click", () => close());
    backdrop.addEventListener("mousedown", event => {
        if (event.target === backdrop) {
            close();
        }
    });
    document.addEventListener("keydown", handleKeydown);

    const instance = { backdrop, dialog, content, close };
    modalStack.push(instance);

    requestAnimationFrame(() => {
        (initialFocus || focusableElements(dialog)[0] || dialog).focus();
    });

    return instance;
}

function createField(field, value) {
    const wrapper = document.createElement("div");
    wrapper.className = `form-field${field.type === "checkbox" ? " form-field-check" : ""}`;

    const inputId = `field-${field.name}`;
    const label = document.createElement("label");
    label.htmlFor = inputId;
    label.textContent = field.label;

    let input;
    let selectControl = null;
    if (field.type === "textarea") {
        input = document.createElement("textarea");
        input.rows = field.rows || 7;
    } else if (field.type === "select") {
        selectControl = createCustomSelect(field, value);
        input = selectControl.valueInput;
    } else {
        input = document.createElement("input");
        input.type = field.type === "checkbox" ? "checkbox" : "text";
    }

    if (field.type !== "select") {
        input.id = inputId;
        input.name = field.name;
        input.required = Boolean(field.required);
    }
    if (field.placeholder) {
        input.placeholder = field.placeholder;
    }
    if (field.maxLength && field.type !== "checkbox" && field.type !== "select") {
        input.maxLength = field.maxLength;
    }

    if (field.type === "checkbox") {
        input.checked = Boolean(value);
        label.prepend(input);
        wrapper.append(label);
    } else {
        if (!selectControl) {
            input.value = value ?? "";
        }
        wrapper.append(label);
    }

    if (field.instructions) {
        const help = document.createElement("p");
        help.className = "field-help";
        help.textContent = field.instructions;
        wrapper.append(help);
    }

    if (selectControl) {
        wrapper.append(selectControl.root);
    } else if (field.type !== "checkbox") {
        wrapper.append(input);
    }

    const error = document.createElement("p");
    error.className = "field-error";
    error.hidden = true;
    error.setAttribute("aria-live", "polite");
    wrapper.append(error);
    return {
        wrapper,
        input,
        error,
        focusTarget: selectControl?.trigger ?? input,
    };
}

function readFormValues(form) {
    const values = {};
    for (const [key, value] of new FormData(form).entries()) {
        values[key] = value;
    }
    for (const checkbox of form.querySelectorAll('input[type="checkbox"]')) {
        values[checkbox.name] = checkbox.checked;
    }
    return values;
}

export function openFormModal({
    title,
    description = "",
    fields,
    initialValues = {},
    submitLabel = "Save",
    cancelLabel = "Cancel",
    validate = null,
    onSubmit,
    onCancel = null,
}) {
    const form = document.createElement("form");
    form.className = "modal-form";
    form.noValidate = true;

    const fieldControls = new Map();
    for (const field of fields) {
        const control = createField(field, initialValues[field.name]);
        fieldControls.set(field.name, { ...control, config: field });
        form.append(control.wrapper);
    }

    const updateConditionalFields = () => {
        const values = readFormValues(form);
        for (const { wrapper, config } of fieldControls.values()) {
            wrapper.hidden = config.visibleWhen
                ? !config.visibleWhen(values)
                : false;
        }
    };
    updateConditionalFields();

    const formError = document.createElement("div");
    formError.className = "form-error-banner";
    formError.setAttribute("role", "alert");
    formError.hidden = true;
    form.append(formError);

    const actions = document.createElement("div");
    actions.className = "modal-actions";
    const cancelButton = document.createElement("button");
    cancelButton.type = "button";
    cancelButton.className = "secondary-button";
    cancelButton.textContent = cancelLabel;
    const submitButton = document.createElement("button");
    submitButton.type = "submit";
    submitButton.className = "primary-button modal-submit";
    submitButton.textContent = submitLabel;
    actions.append(cancelButton, submitButton);
    form.append(actions);

    let modal;
    const cancel = () => {
        modal?.close();
    };
    modal = openModal({
        title,
        description,
        body: form,
        initialFocus: focusableElements(form)[0],
        onClose: onCancel,
    });
    cancelButton.addEventListener("click", cancel);

    for (const { input } of fieldControls.values()) {
        const handleChange = () => {
            formError.hidden = true;
            const control = fieldControls.get(input.name);
            control.error.hidden = true;
            updateConditionalFields();
        };
        input.addEventListener("input", handleChange);
        input.addEventListener("change", handleChange);
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();
        formError.hidden = true;
        let valid = true;

        for (const { input, error, config, wrapper } of fieldControls.values()) {
            error.hidden = true;
            if (
                !wrapper.hidden
                && config.required
                && !String(input.value).trim()
                && config.type !== "checkbox"
            ) {
                error.textContent = `${config.label} is required.`;
                error.hidden = false;
                valid = false;
            }
        }

        if (!valid) {
            fieldControls.values()
                .find(control => !control.error.hidden)
                ?.focusTarget.focus();
            return;
        }

        const values = readFormValues(form);
        const customError = validate?.(values);
        if (customError) {
            formError.textContent = customError;
            formError.hidden = false;
            return;
        }

        submitButton.disabled = true;
        cancelButton.disabled = true;
        submitButton.textContent = "Working...";

        try {
            await onSubmit(values);
            modal.close({ notify: false });
        } catch (error) {
            formError.textContent = error?.message || "The operation could not be completed.";
            formError.hidden = false;
        } finally {
            submitButton.disabled = false;
            cancelButton.disabled = false;
            submitButton.textContent = submitLabel;
        }
    });

    return modal;
}

export function confirmDialog({
    title,
    message,
    confirmLabel = "Confirm",
    cancelLabel = "Cancel",
    destructive = false,
}) {
    return new Promise(resolve => {
        let settled = false;
        const body = document.createElement("div");
        const copy = document.createElement("p");
        copy.className = "confirm-copy";
        copy.textContent = message;
        const actions = document.createElement("div");
        actions.className = "modal-actions";

        const cancel = document.createElement("button");
        cancel.type = "button";
        cancel.className = "secondary-button";
        cancel.textContent = cancelLabel;

        const confirm = document.createElement("button");
        confirm.type = "button";
        confirm.className = destructive ? "danger-button" : "primary-button";
        confirm.textContent = confirmLabel;

        actions.append(cancel, confirm);
        body.append(copy, actions);

        const finish = value => {
            if (settled) {
                return;
            }
            settled = true;
            modal.close({ notify: false });
            resolve(value);
        };

        const modal = openModal({
            title,
            body,
            size: "compact",
            initialFocus: cancel,
            onClose: () => finish(false),
        });

        cancel.addEventListener("click", () => finish(false));
        confirm.addEventListener("click", () => finish(true));
    });
}

export function showToast(message, type = "success") {
    const region = document.getElementById("toast-region");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.setAttribute("role", type === "error" ? "alert" : "status");
    toast.textContent = message;
    region.append(toast);

    requestAnimationFrame(() => toast.classList.add("is-visible"));
    window.setTimeout(() => {
        toast.classList.remove("is-visible");
        window.setTimeout(() => toast.remove(), 220);
    }, 4200);
}
