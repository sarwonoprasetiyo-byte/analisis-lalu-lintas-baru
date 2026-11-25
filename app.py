<!DOCTYPE html>
<html>
<head>
    <title>Video dengan Iklan</title>
</head>
<body>

<video id="video" width="640" controls>
    <source src="video.mp4" type="video/mp4">
</video>

<script>
const video = document.getElementById("");
let sudahKlik = false;

video.addEventListener("play", function(e) {
    if (!sudahKlik) {
        e.preventDefault();
        video.pause();

        sudahKlik = true;

        // Buka halaman iklan
        window.open("https://s.shopee.co.id/LlEukSlwy", "_blank");

        // Putar video setelah 2 detik
        setTimeout(() => {
            video.play();
        }, 2000);
    }
});
</script>

</body>
</html>
