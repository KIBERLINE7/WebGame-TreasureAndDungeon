const forms = document.querySelectorAll("form");

for (const form of forms) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const form_data = new FormData(form);
        const data = {};
        form_data.forEach((value, key) => data[key] = value);

        const res = await fetch(form.action, {
            method: form.method ?? "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        const status = (await res.json()).status;

        if (status === "success") {
            window.location = form.dataset.to;
        }
    })
}