$(document).ready(function () {
  $(".tb-next").click(function () {
    let cur = $(this).closest("#tabArea").find(".tab-pan.active");
    if ($(cur).next().length > 0) {
      $(".tb-prev").removeClass("hide");
      $(".tab-pan").removeClass("active");
      $(cur).next().addClass("active");
    }
    if ($(cur).next().next().length == 0) {
      $(".tb-next").addClass("hide");
      $(".submitbtn").removeClass("hide");
    }
  });

  $(".tb-prev").click(function () {
    let cur = $(this).closest("#tabArea").find(".tab-pan.active");
    if ($(cur).prev().length > 0) {
      $(".submitbtn").addClass("hide");
      $(".tb-next").removeClass("hide");
      $(".tab-pan").removeClass("active");
      $(cur).prev().addClass("active");
    }
    if ($(cur).prev().prev().length == 0) {
      $(".tb-prev").addClass("hide");
    }
  });
});
