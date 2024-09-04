const buttons_rdr = document.querySelectorAll("button.redirect");

for (const btn of buttons_rdr) {
    let url = btn.dataset.to;
    btn.addEventListener("mousedown", async(event) => {

        window.location.replace(url);

    });

}