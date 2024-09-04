const buttons_mr = document.querySelectorAll("button.mr");

let wallet = Number(window.charact.wallet);
let Nick = String(window.charact.nickname);

for (const btn of buttons_mr){
    btn.addEventListener("mousedown", async(event) => {
        const id = Number(btn.dataset.iid);
        const who = Number(btn.dataset.who)
        if (btn.dataset.use === "false"){
            btn.dataset.use = "true";

            let itm;

            if (who === 1) {
                itm = window.inventory.find(item => item.id === id);
            }
            else {
                itm = window.trade.find(item => item.id === id);
            }

            let st = "price" + btn.dataset.iid;
            const p_class = document.getElementsByClassName(st)
            const insert_p = p_class[0];

            let health, def, attack;

            if (itm.buf.health === undefined)
                health = 0;
            else
                health = itm.buf.health;

            if (itm.buf.defend === undefined)
                def = 0;
            else
                def = itm.buf.defend;

            if (itm.buf.attack_point === undefined)
                attack = 0;
            else
                attack = itm.buf.attack_point;

            insert_p.insertAdjacentHTML("afterbegin", '<ul class="inf' + btn.dataset.iid + '"><li>Здоровье: +' + health + '</li><li>Атака: +' + attack + '</li><li>Защита: +' + def + '</li></ul>');
        }
        else {

            btn.dataset.use = "false";

            let st = "inf" + btn.dataset.iid;
            const ul_class = document.getElementsByClassName(st)

            const remove_ul = ul_class[0];

            remove_ul.remove();

        }
    });

}