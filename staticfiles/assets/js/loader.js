window.addEventListener("load", function () {
    const loadingScreen = document.getElementById("loading-screen");
    const mainContent = document.getElementById("main-content");

    loadingScreen.style.opacity = 1;
    const fadeEffect = setInterval(() => {
        if (loadingScreen.style.opacity > 0) {
            loadingScreen.style.opacity -= 0.1;
        } else {
            clearInterval(fadeEffect);
            loadingScreen.style.display = "none";
            mainContent.style.display = "block";
        }
    }, 50);
});
