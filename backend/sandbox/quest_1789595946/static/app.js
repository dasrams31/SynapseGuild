document.addEventListener('DOMContentLoaded', () => {
    // Navigation Tab Switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-tab');
            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            btn.classList.add('active');
            const activePane = document.getElementById(target);
            if (activePane) {
                activePane.classList.add('active');
            }
        });
    });

    // Calculator Form Submission
    const form = document.getElementById('nutrition-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                gender: document.getElementById('gender').value,
                age: parseInt(document.getElementById('age').value, 10),
                weight: parseFloat(document.getElementById('weight').value),
                height: parseFloat(document.getElementById('height').value),
                activity_level: document.getElementById('activity_level').value,
                goal: document.getElementById('goal').value,
                diet_type: document.getElementById('diet_type').value
            };

            try {
                const response = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const err = await response.json();
                    alert('Calculation error: ' + (err.error || 'Server error'));
                    return;
                }

                const data = await response.json();
                updateResultsUI(data);
            } catch (err) {
                console.error('Error fetching calculation:', err);
            }
        });
    }

    function updateResultsUI(data) {
        document.getElementById('res-bmi').textContent = data.bmi;
        document.getElementById('res-bmi-class').textContent = data.bmi_classification;
        document.getElementById('res-bmr').textContent = Math.round(data.bmr);
        document.getElementById('res-tdee').textContent = Math.round(data.tdee);
        document.getElementById('res-calories').textContent = Math.round(data.target_calories);

        const macros = data.macros;
        document.getElementById('res-protein').textContent = `${macros.protein_g}g (${macros.percentage.protein}%)`;
        document.getElementById('res-carbs').textContent = `${macros.carbs_g}g (${macros.percentage.carbs}%)`;
        document.getElementById('res-fat').textContent = `${macros.fat_g}g (${macros.percentage.fat}%)`;

        document.getElementById('bar-protein').style.width = `${macros.percentage.protein}%`;
        document.getElementById('bar-carbs').style.width = `${macros.percentage.carbs}%`;
        document.getElementById('bar-fat').style.width = `${macros.percentage.fat}%`;

        document.getElementById('res-water').textContent = `${data.water_intake_liters} L`;

        const tipsList = document.getElementById('res-tips-list');
        tipsList.innerHTML = '';
        if (data.recommended_tips && data.recommended_tips.length > 0) {
            data.recommended_tips.forEach(tip => {
                const li = document.createElement('li');
                li.textContent = tip;
                tipsList.appendChild(li);
            });
        }

        // Also synchronize meal plan calories input
        const planCaloriesInput = document.getElementById('plan-calories');
        if (planCaloriesInput) {
            planCaloriesInput.value = Math.round(data.target_calories);
        }
    }

    // Tips Library Logic
    let cachedTips = {};
    async function loadTips() {
        try {
            const response = await fetch('/api/tips');
            const data = await response.json();
            cachedTips = data.tips || {};
            renderTips('all');
        } catch (err) {
            console.error('Failed to load tips:', err);
        }
    }

    function renderTips(category) {
        const container = document.getElementById('full-tips-grid');
        if (!container) return;
        container.innerHTML = '';

        Object.keys(cachedTips).forEach(cat => {
            if (category === 'all' || category === cat) {
                cachedTips[cat].forEach(tipText => {
                    const card = document.createElement('div');
                    card.className = `tip-card ${cat}`;
                    card.innerHTML = `
                        <h4>${cat.replace('_', ' ')}</h4>
                        <p>${tipText}</p>
                    `;
                    container.appendChild(card);
                });
            }
        });
    }

    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderTips(btn.getAttribute('data-category'));
        });
    });

    // Meal Planner Logic
    const genPlanBtn = document.getElementById('gen-plan-btn');
    if (genPlanBtn) {
        genPlanBtn.addEventListener('click', async () => {
            const calories = parseFloat(document.getElementById('plan-calories').value) || 2000;
            const diet = document.getElementById('plan-diet').value;

            try {
                const response = await fetch('/api/meal-plan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ calories, diet_type: diet })
                });

                if (!response.ok) {
                    alert('Error generating meal plan');
                    return;
                }

                const data = await response.json();
                renderMealPlan(data.meal_plan);
            } catch (err) {
                console.error('Meal plan fetch error:', err);
            }
        });
    }

    function renderMealPlan(plan) {
        const summary = document.getElementById('meal-plan-summary');
        const container = document.getElementById('meals-container');
        if (!summary || !container) return;

        summary.innerHTML = `
            <strong>Plan Summary:</strong> ${plan.actual_calories} Total kcal &bull; 
            Protein: ${plan.total_protein_g}g &bull; 
            Carbs: ${plan.total_carbs_g}g &bull; 
            Fats: ${plan.total_fat_g}g
        `;

        container.innerHTML = '';
        plan.meals.forEach(meal => {
            const box = document.createElement('div');
            box.className = 'meal-box';
            box.innerHTML = `
                <div class="meal-box-header">
                    <span class="meal-title">${meal.meal}</span>
                    <span class="meal-cals">${meal.calories} kcal</span>
                </div>
                <div class="meal-item">${meal.item}</div>
                <div class="meal-macros-tag">
                    <span>P: ${meal.protein_g}g</span>
                    <span>C: ${meal.carbs_g}g</span>
                    <span>F: ${meal.fat_g}g</span>
                </div>
            `;
            container.appendChild(box);
        });
    }

    // Initial bootstrap calls
    loadTips();
    if (form) {
        form.dispatchEvent(new Event('submit'));
    }
});
