function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const buttons_upd = document.querySelectorAll("button.upd");
const divs = document.querySelectorAll("div.item");
const pars = document.querySelectorAll("p.health");
const divs_enemy = document.querySelectorAll("div.enemy");

for (const button of buttons_upd){
    button.addEventListener("mousedown", async(event) => {

        const data = {};

        if (button.dataset.op !== undefined) {

            data[button.dataset.op] = Number(button.dataset.iid);

        }
        const res = await fetch(button.dataset.to, {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        request = (await res.json());
        status = request.status;

        if (status !== "success"){

            if (status === "finish") {
                window.alert("Вы победили в поздемелье ! Внимание переход в инвентарь...");
                window.location.replace("/pages/inventory");

            }
            else if (status === "next") {
                id = Number(button.dataset.iid);

                const enemy = window.enemys.find(enemy => enemy.id === id);

                let p_edit_health_enemy = Number(enemy.health), p_edit_health_character = Number(window.charact.health),
                character_defend = Number(window.charact.defend);
                let character_attack = Number(window.charact.attack_point);
                let enemy_defend = Number(enemy.defend);

                if (character_attack > enemy_defend) {
                    p_edit_health_enemy -= (character_attack - enemy_defend);
                }
                else {
                    p_edit_health_enemy -= 1;
                }


                enemy.health = p_edit_health_enemy;

                find_str = "health-" + button.dataset.iid;
                let edit_par ;
                for (const par of pars){
                    if (par.dataset.iid === find_str) {
                        edit_par = par;
                        break;
                    }
                }

                edit_par.innerText = "Здоровье: " + String(enemy.health);

                find_str = "div-" + button.dataset.iid;
                let edit_div ;
                for (const div of divs_enemy){
                    if (div.dataset.iid === find_str) {
                        edit_div = div;
                        break;
                    }
                }
                if (enemy.health <= 0){
                    edit_div.remove();

                    let idx = window.enemys.findindex(enemy => enemy.id === id);
                    window.enemys.splice(idx, 1);

                }

                window.alert("Начинается ход противника");

                for (const attacking_enemy of window.enemys) {

                    const data = {};

                    data['enemy_id'] = Number(attacking_enemy.id);

                    const res = await fetch("/dungeon/battle/defend", {
                        method: "PATCH",
                        headers: {
                          "Content-Type": "application/json",
                        },
                        body: JSON.stringify(data),
                    });
                    request = (await res.json());
                    status = request.status;

                    if (status === "died") {

                        window.alert("Вы умери в подземелье....Перенос в хаб.");
                        window.location.replace("/pages/inventory");


                    }
                    else if (status === "damageOK") {
                        let attack_enemy = attacking_enemy.attack_point;
                        if ( character_defend == attack_enemy) {
                            p_edit_health_character -= 1;
                        }
                        else if (character_defend < attack_enemy) {
                            p_edit_health_character -= (attack_enemy - character_defend);
                        }

                        window.charact.health = p_edit_health_character;
                        p_health_charact = document.getElementById("health-charct");

                        p_health_charact.innerText = "Здоровье: " + String(window.charact.health) ;


                    }
                    else {

                        window.alert("Ошибка");

                    }

                }



            }

            else {

                window.alert("Ошибка")

            }
        }
        else{
            if (button.dataset.oph === "sell" || button.dataset.oph === "buy"){
                id = Number(button.dataset.iid);
                find_str = "div-" + button.dataset.iid;
                let replace_div ;
                for (const div of divs){
                    if (div.dataset.iid === find_str) {
                        replace_div = div;
                        break;
                    }
                }
                let past_div = replace_div;
                replace_div.remove();

                const div_wallet = document.getElementById("edge");

                if (button.dataset.oph === "sell"){
                    let itm = window.inventory.find(item => item.id === id);
                    const insert_div = document.getElementById("trader_container");
                    insert_div.insertAdjacentElement("beforeend", past_div);

                    wallet += Number(itm.price);

                    div_wallet.innerText = Nick + ": " +  String(wallet);
                    let idx = window.trade.findIndex(item => item.id === id);
                    window.inventory.splice(idx, 1);
                    window.trade.push(itm);

                    button.dataset.to = "/trader/market/buy";
                    button.dataset.oph = "buy";
                    button.innerText = "Купить";

                }
                else{
                    if (button.dataset.oph === "buy"){
                        let itm = window.trade.find(item => item.id === id);
                        const insert_div = document.getElementById("character_container");
                        insert_div.insertAdjacentElement("beforeend", past_div);

                        wallet -= Number(itm.price);

                        div_wallet.innerText = Nick + ": " + String(wallet);

                        let idx = window.trade.findIndex(item => item.id === id);
                        window.trade.splice(idx, 1);
                        window.inventory.push(itm);

                        button.dataset.to = "/trader/market/sell";
                        button.dataset.oph = "sell";
                        button.innerText = "Продать";

                    }
                    else {

                        location.reload();

                    }
                }

            }
            else if (button.dataset.oph === "leave") {

                window.location.replace(button.dataset.redir);

            }
            else if (button.dataset.oph === "todungeon") {

                window.location.replace(button.dataset.redir);

            }
            else if (button.dataset.oph === "logout") {

                window.location.replace(button.dataset.redir);

            }
            else if (button.dataset.oph === "levelup") {

                window.alert("Ваш уровень повышен !!");
                location.reload();

            }
        }

    });
}