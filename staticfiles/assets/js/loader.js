window.addEventListener("load", function () {
    const loadingScreen = document.getElementById("loader-wrapper");
    const mainContent = document.getElementById("main-wrapper");

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
