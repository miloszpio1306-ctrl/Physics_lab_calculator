const DEFAULT_TABS = [
    {
        id: 'em_excel',
        title: 'Cw. 45: B oraz e/m (Tabela 20 pkt - Excel)',
        builtin: true,
        calcMode: 'point_by_point',
        kFactor: '1',
        targets: [
            {
                symbol: 'e_m',
                unit: 'C/kg',
                formula: '125 * U * R**2 / (32 * mu_0**2 * n**2 * I**2 * r**2)',
                ref_value: '1.75882e11'
            },
            {
                symbol: 'B',
                unit: 'T',
                formula: '(4/5)**(3/2) * mu_0 * n * I / R',
                ref_value: ''
            }
        ],
        variables: [
            {name:'U', unit:'V', raw_values:'75; 75; 75; 75; 100; 100; 100; 100; 150; 150; 150; 150; 200; 200; 200; 200; 250; 250; 250; 250', delta:'0.5', dist_type:'direct'},
            {name:'r', unit:'m', raw_values:'0.02; 0.03; 0.04; 0.05; 0.02; 0.03; 0.04; 0.05; 0.02; 0.03; 0.04; 0.05; 0.02; 0.03; 0.04; 0.05; 0.02; 0.03; 0.04; 0.05', delta:'0.005', dist_type:'direct'},
            {name:'I', unit:'A', raw_values:'2.67; 1.74; 1.25; 0.98; 3.29; 2.01; 1.49; 1.15; 3.69; 2.37; 1.73; 1.37; 4.00; 2.57; 1.89; 1.49; 4.15; 2.83; 2.06; 1.64', delta:'0.01', dist_type:'direct'},
            {name:'R', unit:'m', raw_values:'0.2', delta:'0.01', dist_type:'direct'},
            {name:'n', unit:'1', raw_values:'154', delta:'0', dist_type:'direct'}
        ]
    },
    {
        id: 'em_single',
        title: 'Cw. 45: Pojedyncza kolumna (U=200V, r=4cm)',
        builtin: true,
        calcMode: 'mean_first',
        kFactor: '1',
        targets: [
            {
                symbol: 'B',
                unit: 'T',
                formula: '(4/5)**(3/2) * mu_0 * n * I / R',
                ref_value: ''
            },
            {
                symbol: 'e_m',
                unit: 'C/kg',
                formula: '2 * U / (B**2 * r**2)',
                ref_value: '1.75882e11'
            }
        ],
        variables: [
            {name:'U', unit:'V', raw_values:'200', delta:'0.5', dist_type:'direct'},
            {name:'r', unit:'m', raw_values:'0.04', delta:'0.005', dist_type:'direct'},
            {name:'I', unit:'A', raw_values:'1.89', delta:'0.01', dist_type:'direct'},
            {name:'R', unit:'m', raw_values:'0.2', delta:'0.01', dist_type:'direct'},
            {name:'n', unit:'1', raw_values:'154', delta:'0', dist_type:'direct'}
        ]
    },
    {
        id: 'gravity',
        title: 'Wahadlo matematyczne (g)',
        builtin: true,
        calcMode: 'mean_first',
        kFactor: '1',
        targets: [
            {
                symbol: 'g',
                unit: 'm/s^2',
                formula: '4 * pi**2 * l / T**2',
                ref_value: '9.8105'
            }
        ],
        variables: [
            {name:'l', unit:'m', raw_values:'0.852', delta:'0.001', dist_type:'uniform'},
            {name:'T', unit:'s', raw_values:'1.851; 1.854; 1.849; 1.852; 1.850', delta:'0.002', dist_type:'uniform'}
        ]
    }
];

let tabs = [];
let activeTabId = 'em_excel';

function toggleDrawer(drawerId, btnId) {
    const drawer = document.getElementById(drawerId);
    const btn = document.getElementById(btnId);
    const isOpen = drawer.classList.contains('open');
    drawer.classList.toggle('open', !isOpen);
    btn.classList.toggle('active', !isOpen);
}

function renderEmptyRightColumn() {
    document.getElementById('errorBox').style.display = 'none';
    document.getElementById('resultsContent').innerHTML = `
        <div class="empty-state-box">
            <div class="empty-state-title">Brak wynikow do wyswietlenia</div>
            <div style="font-size:0.84rem;">
                Uzupelnij wzor szukanej wielkosci oraz wartosci zmiennych po lewej stronie, a nastepnie kliknij przycisk <b>Przelicz wszystkie szukane wielkosci</b>.
            </div>
            <div class="empty-kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Wartosc srednia</div>
                    <div class="kpi-main" style="color:var(--muted);">—</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Niepewnosc ostateczna (u_c)</div>
                    <div class="kpi-main" style="color:var(--muted);">—</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Niepewnosc typu A (u_A)</div>
                    <div class="kpi-main" style="color:var(--muted);">—</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Niepewnosc typu B (u_B)</div>
                    <div class="kpi-main" style="color:var(--muted);">—</div>
                </div>
            </div>
        </div>
    `;
}

function initTabs() {
    const saved = localStorage.getItem('fizyka_calc_tabs_v40');
    if (saved) {
        try {
            const customTabs = JSON.parse(saved);
            tabs = [...DEFAULT_TABS, ...customTabs];
        } catch (e) {
            tabs = [...DEFAULT_TABS];
        }
    } else {
        tabs = [...DEFAULT_TABS];
    }
    renderTabsBar();
    selectTab(activeTabId);
}

function saveCustomTabsToStorage() {
    const customTabs = tabs.filter(t => !t.builtin);
    localStorage.setItem('fizyka_calc_tabs_v40', JSON.stringify(customTabs));
}

function renderTabsBar() {
    const bar = document.getElementById('tabsBar');
    bar.innerHTML = '';
    tabs.forEach(t => {
        const pill = document.createElement('div');
        pill.className = 'tab-pill' + (t.id === activeTabId ? ' active' : '');
        pill.onclick = () => selectTab(t.id);

        const titleSpan = document.createElement('span');
        titleSpan.textContent = t.title;
        pill.appendChild(titleSpan);

        if (!t.builtin) {
            const closeBtn = document.createElement('span');
            closeBtn.className = 'tab-close';
            closeBtn.textContent = 'x';
            closeBtn.title = 'Usun zakladke';
            closeBtn.onclick = (ev) => {
                ev.stopPropagation();
                deleteCustomTab(t.id);
            };
            pill.appendChild(closeBtn);
        }
        bar.appendChild(pill);
    });
}

function selectTab(id) {
    const t = tabs.find(x => x.id === id) || tabs[0];
    activeTabId = t.id;
    document.getElementById('currentTabLabel').textContent = 'Aktywne: ' + t.title;
    renderTabsBar();

    document.getElementById('calcMode').value = t.calcMode || 'mean_first';
    document.getElementById('kFactor').value = t.kFactor || '1';

    const tc = document.getElementById('targetsContainer');
    tc.innerHTML = '';
    const targetsList = t.targets && t.targets.length
        ? t.targets
        : [{symbol: '', unit: '', formula: '', ref_value: ''}];
    targetsList.forEach(item => addTargetFormula(item));

    const vc = document.getElementById('variablesContainer');
    vc.innerHTML = '';
    const varsList = t.variables && t.variables.length
        ? t.variables
        : [{name: '', unit: '', raw_values: '', delta: '0', dist_type: 'uniform'}];
    varsList.forEach(v => addVariable(v));

    // Sprawdzamy, czy zakladka ma wypelniony wzor i zmienne - jesli nie (nowa zakladka), czyscimy prawa kolumne!
    const hasFormula = targetsList.some(x => x.formula && x.formula.trim() !== '');
    const hasVars = varsList.some(v => v.name && v.name.trim() !== '' && v.raw_values && v.raw_values.trim() !== '');

    if (hasFormula && hasVars) {
        calculatePropagation();
    } else {
        renderEmptyRightColumn();
    }
}

function readCurrentFormState() {
    const targets = [];
    document.querySelectorAll('.target-box').forEach(b => {
        targets.push({
            symbol: b.querySelector('.t-symbol').value,
            unit: b.querySelector('.t-unit').value,
            formula: b.querySelector('.t-formula').value,
            ref_value: b.querySelector('.t-ref').value
        });
    });

    const variables = [];
    document.querySelectorAll('.var-box').forEach(b => {
        variables.push({
            name: b.querySelector('.v-name').value,
            unit: b.querySelector('.v-unit').value,
            raw_values: b.querySelector('.v-raw').value,
            delta: b.querySelector('.v-delta').value,
            dist_type: b.querySelector('.v-dist').value
        });
    });

    return {
        calcMode: document.getElementById('calcMode').value,
        kFactor: document.getElementById('kFactor').value,
        targets: targets,
        variables: variables
    };
}

function createNewCustomTab() {
    const name = prompt("Podaj nazwe nowej zakladki (np. CW82):", "CW" + (tabs.length + 1));
    if (!name) return;
    const newId = 'custom_' + Date.now();
    // Nowa zakladka jest zawsze w 100% pusta!
    tabs.push({
        id: newId,
        title: name,
        builtin: false,
        calcMode: 'mean_first',
        kFactor: '1',
        targets: [{symbol: '', unit: '', formula: '', ref_value: ''}],
        variables: [{name: '', unit: '', raw_values: '', delta: '0', dist_type: 'uniform'}]
    });
    saveCustomTabsToStorage();
    selectTab(newId);
}

function saveCurrentTab() {
    const idx = tabs.findIndex(t => t.id === activeTabId);
    if (idx === -1) return;
    const state = readCurrentFormState();
    if (tabs[idx].builtin) {
        const name = prompt("Zapisujesz zmodyfikowana wersje jako nowa zakladke. Podaj nazwe:", tabs[idx].title + " (Wlasne)");
        if (!name) return;
        const newId = 'custom_' + Date.now();
        tabs.push({ id: newId, title: name, builtin: false, ...state });
        activeTabId = newId;
    } else {
        tabs[idx] = { ...tabs[idx], ...state };
    }
    saveCustomTabsToStorage();
    renderTabsBar();
}

function autoSaveDraft() {
    const idx = tabs.findIndex(t => t.id === activeTabId);
    if (idx !== -1 && !tabs[idx].builtin) {
        tabs[idx] = { ...tabs[idx], ...readCurrentFormState() };
        saveCustomTabsToStorage();
    }
}

function deleteCustomTab(id) {
    if (!confirm("Czy na pewno chcesz usunac te zakladke?")) return;
    tabs = tabs.filter(t => t.id !== id);
    saveCustomTabsToStorage();
    if (activeTabId === id) {
        selectTab(tabs[0].id);
    } else {
        renderTabsBar();
    }
}

function addTargetFormula(data) {
    data = data || {symbol: '', unit: '', formula: '', ref_value: ''};
    const container = document.getElementById('targetsContainer');
    const div = document.createElement('div');
    div.className = 'target-box';
    div.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <strong style="color:var(--success); font-size:0.82rem; text-transform:uppercase;">Szukana wielkosc (Wzor)</strong>
            <button class="btn-danger" onclick="if(document.querySelectorAll('.target-box').length>1){this.parentElement.parentElement.remove(); autoSaveDraft();}">Usun wzor</button>
        </div>
        <div class="row">
            <div>
                <label>Szukany symbol (np. B, e_m)</label>
                <input type="text" class="t-symbol" value="${data.symbol}" placeholder="np. e_m" style="font-weight:800;" oninput="autoSaveDraft()">
            </div>
            <div>
                <label>Jednostka wyniku</label>
                <input type="text" class="t-unit" value="${data.unit}" placeholder="np. C/kg, T" oninput="autoSaveDraft()">
            </div>
            <div>
                <label>Wartosc tablicowa (opcjonalnie)</label>
                <input type="text" class="t-ref" value="${data.ref_value}" placeholder="np. 1.75882e11" oninput="autoSaveDraft()">
            </div>
        </div>
        <div>
            <label>Wzor pomiarowy (mozesz uzywac zmiennych z sekcji 2 oraz symboli z powyzszych wzorow)</label>
            <input type="text" class="t-formula" value="${data.formula}" placeholder="np. 2 * U / (B**2 * r**2)" style="font-family:monospace; font-weight:700; color:var(--accent);" oninput="autoSaveDraft()">
        </div>
    `;
    container.appendChild(div);
}

function addVariable(data) {
    data = data || {name: '', unit: '', raw_values: '', delta: '0', dist_type: 'uniform'};
    const container = document.getElementById('variablesContainer');
    const div = document.createElement('div');
    div.className = 'var-box';
    div.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <strong style="color:var(--accent); font-size:0.82rem; text-transform:uppercase;">Zmienna pomiarowa</strong>
            <button class="btn-danger" onclick="if(document.querySelectorAll('.var-box').length>1){this.parentElement.parentElement.remove(); autoSaveDraft();}">Usun</button>
        </div>
        <div class="row">
            <div><label>Symbol</label><input type="text" class="v-name" value="${data.name}" placeholder="np. U, I, r" style="font-weight:800;" oninput="autoSaveDraft()"></div>
            <div><label>Jednostka</label><input type="text" class="v-unit" value="${data.unit}" placeholder="np. V, A, m" oninput="autoSaveDraft()"></div>
            <div>
                <label>Sposob liczenia u_B(x)</label>
                <select class="v-dist" onchange="autoSaveDraft()">
                    <option value="direct" ${data.dist_type==='direct'?'selected':''}>Bezposrednio u(x) (jak w Excelu)</option>
                    <option value="uniform" ${data.dist_type==='uniform'?'selected':''}>Rozklad jednostajny: dx / sqrt(3)</option>
                </select>
            </div>
            <div><label>Niepewnosc u(x) / dx</label><input type="text" class="v-delta" value="${data.delta}" style="font-weight:700;" oninput="autoSaveDraft()"></div>
        </div>
        <div>
            <label>Wartosci (pojedyncza wartosc lub seria oddzielona srednikiem ';')</label>
            <input type="text" class="v-raw" value="${data.raw_values}" placeholder="np. 12.1; 12.3; 12.2" oninput="autoSaveDraft()">
        </div>
    `;
    container.appendChild(div);
}

function fmtExcel(num) {
    if (num === 0) return "0";
    if (Math.abs(num) >= 1e4 || Math.abs(num) < 1e-2) {
        return num.toExponential(1).replace('.', ',').replace('e+', 'E+').replace('e-', 'E-');
    }
    return Number(num.toPrecision(3)).toString().replace('.', ',');
}

function fmtExact(num) {
    if (num === 0) return "0";
    if (Math.abs(num) >= 1e4 || Math.abs(num) < 1e-2) {
        return num.toExponential(3).replace('.', ',');
    }
    return Number(num.toPrecision(5)).toString().replace('.', ',');
}

async function calculatePropagation() {
    autoSaveDraft();
    const errBox = document.getElementById('errorBox');
    errBox.style.display = 'none';
    const state = readCurrentFormState();

    const payload = {
        calc_mode: state.calcMode,
        k_factor: state.kFactor,
        sig_digits: 2,
        targets: state.targets,
        variables: state.variables
    };

    try {
        const res = await fetch('/api/calculate', {
            method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)
        });
        const respData = await res.json();
        if (!res.ok || respData.error) throw new Error(respData.error || 'Blad obliczen');

        const resultsList = respData.targets_results || [];
        if (!resultsList.length) {
            renderEmptyRightColumn();
            return;
        }

        let allHtml = '';

        resultsList.forEach((d, idx) => {
            const unitStr = d.target_unit ? `[${d.target_unit}]` : '';
            const isOpenAttr = idx === 0 ? 'open' : '';

            allHtml += `
            <details class="target-result-tab" ${isOpenAttr}>
                <summary>
                    <div class="target-tab-title">
                        Wynik ${idx + 1}: <span>${d.target_symbol} = ${d.formatted_expanded} ${unitStr}</span>
                    </div>
                    <div class="target-tab-badge">
                        Excel: ${fmtExcel(d.y_val)} +/- ${fmtExcel(d.u_exp_y)} (Rozwin / Zwin ▾)
                    </div>
                </summary>
                <div class="target-tab-body">
                    <div class="hero-result">
                        <div class="hero-label">Wzor: <code>${d.target_symbol} = ${d.formula_str}</code> (k = ${d.k_factor}, niepewnosc wzgledna = <strong>${d.rel_y_pct.toFixed(1)}%</strong>)</div>
                        <div class="hero-value">${d.target_symbol} = <span>${d.formatted_expanded}</span> ${unitStr}</div>
                        <div class="hero-sub">
                            Zapis w formacie Twojego Excela: <strong>${fmtExcel(d.y_val)} +/- ${fmtExcel(d.u_exp_y)} ${unitStr}</strong>
                        </div>
                    </div>

                    <div class="kpi-grid">
                        <div class="kpi-card highlight">
                            <div class="kpi-title">Wartosc srednia (${d.target_symbol} sr)</div>
                            <div class="kpi-main green">${fmtExcel(d.y_val)} <span style="font-size:0.8rem; font-weight:600;">${unitStr}</span></div>
                            <div class="kpi-exact">Dokladnie: <strong>${fmtExact(d.y_val)}</strong></div>
                        </div>
                        <div class="kpi-card highlight">
                            <div class="kpi-title">Niepewnosc ostateczna (u_c)</div>
                            <div class="kpi-main blue">${fmtExcel(d.u_c_y)} <span style="font-size:0.8rem; font-weight:600;">${unitStr}</span></div>
                            <div class="kpi-exact">Dokladnie: <strong>${fmtExact(d.u_c_y)}</strong></div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Niepewnosc typu A (u_A)</div>
                            <div class="kpi-main">${fmtExcel(d.u_a_y)}</div>
                            <div class="kpi-exact">Dokladnie: <strong>${fmtExact(d.u_a_y)}</strong></div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Niepewnosc typu B (u_B)</div>
                            <div class="kpi-main">${fmtExcel(d.u_b_y)}</div>
                            <div class="kpi-exact">Dokladnie: <strong>${fmtExact(d.u_b_y)}</strong></div>
                        </div>
                    </div>
            `;

            if (d.ref_comparison) {
                const rc = d.ref_comparison;
                let boxClass = 'ok';
                let statusTitle = `ZGODNY: Wynik miesci sie w granicach niepewnosci (dla k = ${rc.k_factor})`;
                let extraHint = '';

                if (!rc.fits_k) {
                    if (rc.fits_2) {
                        boxClass = 'warn';
                        statusTitle = `CZESCIOWO ZGODNY: Nie miesci sie w 1*u_c, ale MIESCI SIE w niepewnosci rozszerzonej 2*u_c`;
                        extraHint = `<div style="margin-top:6px;"><strong>Wniosek:</strong> Roznica od wartosci tablicowej wynosi <strong>${rc.z_score.toFixed(2)} * u_c</strong>. Po przejsciu na niepewnosc rozszerzona (k = 2) wynik pokrywa wartosc tablicowa.</div>`;
                    } else {
                        boxClass = 'fail';
                        statusTitle = `NIEZGODNY: Wynik nie miesci sie w niepewnosci (roznica wynosi ${rc.z_score.toFixed(2)} * u_c)`;
                        extraHint = `<div style="margin-top:6px;"><strong>Wniosek:</strong> Wartosc tablicowa lezy poza przedzialem niepewnosci pomiarowej.</div>`;
                    }
                }

                allHtml += `
                    <div class="fit-box ${boxClass}">
                        <div class="fit-header">${statusTitle}</div>
                        <div class="fit-details">
                            <div>Wartosc tablicowa: <strong>${fmtExact(rc.ref_val)} ${unitStr}</strong> (blad wzgledny od tablicowej: <strong>${rc.rel_diff_pct.toFixed(1)}%</strong>)</div>
                            <div>Przedzial pomiarowy [${d.target_symbol} - ${rc.k_factor}*u_c ; ${d.target_symbol} + ${rc.k_factor}*u_c]: <strong>[ ${fmtExact(rc.lower_bound)} ; ${fmtExact(rc.upper_bound)} ] ${unitStr}</strong></div>
                            <div>Roznica |y - y_tab|: <strong>${fmtExcel(rc.diff)}</strong> wobec niepewnosci (${rc.k_factor}*u_c): <strong>${fmtExcel(rc.u_exp)}</strong></div>
                            ${extraHint}
                        </div>
                    </div>
                `;
            }

            const domText = d.dominant_source ? `Glowny wklad: ${d.dominant_source.name} (${d.dominant_source.share_pct.toFixed(1)}%)` : 'Rozwin';

            allHtml += `
                <details class="accordion">
                    <summary>
                        <span>Budzet niepewnosci i pochodne czastkowe dla ${d.target_symbol}</span>
                        <span class="acc-badge"><strong>${domText}</strong> ▾</span>
                    </summary>
                    <div class="accordion-body">
                        <table>
                            <thead><tr><th>Zmienna</th><th>Pochodna czastkowa df/dx_i</th><th>Udzial w niepewnosci</th></tr></thead>
                            <tbody>`;
            d.partials.forEach(p => {
                const isDom = d.dominant_source && d.dominant_source.name === p.name && p.share_pct > 50;
                allHtml += `<tr style="${isDom ? 'background:rgba(56,189,248,0.12);' : ''}">
                    <td><strong>${p.name}</strong></td>
                    <td><code>${p.derivative_expr}</code></td>
                    <td><strong>${p.share_pct.toFixed(1)}%</strong></td>
                </tr>`;
            });
            allHtml += `</tbody></table></div></details>`;

            if (d.point_rows) {
                allHtml += `
                <details class="accordion">
                    <summary>
                        <span>Tabela wszystkich ${d.point_rows.length} kolumn pomiarowych dla ${d.target_symbol}</span>
                        <span class="acc-badge">Pokaz ${d.point_rows.length} pomiarow ▾</span>
                    </summary>
                    <div class="accordion-body" style="max-height:300px; overflow-y:auto;">
                        <table>
                            <thead><tr><th>Kol.</th><th>Dane wejsciowe</th><th>${d.target_symbol} (Excel)</th><th>Niep B (Excel)</th><th>${d.target_symbol} (dokladnie)</th></tr></thead>
                            <tbody>`;
                d.point_rows.forEach(r => {
                    const kv = Object.entries(r.vals).map(([k,v]) => `${k}=${v}`).join(', ');
                    allHtml += `<tr>
                        <td><b>#${r.idx}</b></td>
                        <td>${kv}</td>
                        <td><strong style="color:var(--success);">${fmtExcel(r.y)}</strong></td>
                        <td><strong style="color:var(--accent);">${fmtExcel(r.u_b)}</strong></td>
                        <td style="color:var(--muted);">${fmtExact(r.y)}</td>
                    </tr>`;
                });
                allHtml += `</tbody></table></div></details>`;
            }

            allHtml += `
                <details class="accordion">
                    <summary>
                        <span>Gotowy kod LaTeX dla ${d.target_symbol}</span>
                        <span class="acc-badge">Rozwin i skopiuj ▾</span>
                    </summary>
                    <div class="accordion-body">
                        <textarea rows="8" readonly style="font-family:monospace; font-size:0.78rem;">${d.latex_report}</textarea>
                    </div>
                </details>
                </div>
            </details>`;
        });

        document.getElementById('resultsContent').innerHTML = allHtml;
    } catch (e) {
        // Jesli wystapil blad, zawsze czyscimy stare wyniki po prawej stronie!
        renderEmptyRightColumn();
        errBox.textContent = "BLAD: " + e.message;
        errBox.style.display = 'block';
    }
}

window.addEventListener('DOMContentLoaded', initTabs);
