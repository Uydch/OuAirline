

$(document).ready(function(){
$(window).scroll(function(){
if ($(this).scrollTop() >=50){
    $("nav.navbar").css({
        "position":"fixed",
        "z-index":2,
        "top":0,
        "left":0,
        "right":0,
        "opacity":0.95
    })

}
else
$("nav.navbar").css({
    "position":"relative",
    "opacity":1
})

 $(window).scroll(function(){
     if ($(this).scrollTop() >=200){
         $(".btns").addClass("animate__animated animate__fadeInUp")}
     else{
         $(".btns").removeClass("animate__animated animate__fadeInUp")}
 })
 $(".btns").click(function(){
     $("body").animate({
         scrollTop:0
     },1000)
 })

}

window.addEventListener('load', checkFooterPosition);
window.addEventListener('resize', checkFooterPosition);

function checkFooterPosition() {
    const footer = document.querySelector('.footer');
    const body = document.body;
    const html = document.documentElement;

    const docHeight = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
    const windowHeight = window.innerHeight;

    // Nếu chiều cao trang nhỏ hơn chiều cao cửa sổ, footer sẽ cố định
    if (docHeight < windowHeight) {
        footer.classList.add('fixed');
    } else {
        footer.classList.remove('fixed');
    }
}

