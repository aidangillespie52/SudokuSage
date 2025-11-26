// frontend/static/js/walkthrough.js

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("difficulty-modal");
    const tourBtn = document.getElementById("btn-tour");

    function startTour() {
        const intro = introJs().setOptions({
            showProgress: true,
            showBullets: false,
            exitOnOverlayClick: false,
        });

        let step = 0; // step = 1 so step===3 matches your data-step="3"

        intro.onchange(function () {
            console.log("Current step:", step);

            if (step === 3) {
                modal.classList.remove("hidden");    // SHOW after step 3
            } 
            if (step === 5) {
                modal.classList.add("hidden");       // HIDE after step 4
            }

            step += 1;
        });

        intro.oncomplete(function () {
            modal.classList.add("hidden");
            localStorage.setItem("sudoku_tour_done", "1");
        });

        intro.onexit(function () {
            modal.classList.add("hidden");
            localStorage.setItem("sudoku_tour_done", "1");
        });

        intro.start();
    }

    // Run automatically on first visit
    if (!localStorage.getItem("sudoku_tour_done")) {
        startTour();
    }

    // Tour button replays the walkthrough any time
    if (tourBtn) {
        tourBtn.addEventListener("click", function () {
            modal.classList.add("hidden"); // reset state
            startTour();
        });
    }
});
