$(function scroller() 
{
  //pane,paneContent
//change the main div to overflow-hidden as we can use the slider now
$('#scroll-pane').css('overflow','hidden');

//compare the height of the scroll content to the scroll pane to see if we need a scrollbar
var difference = $('#updates2').height()-$('#scroll-pane').height();//eg it's 200px longer 

if(difference>0)//if the scrollbar is needed, set it up...
{
   var proportion = difference / $('#updates2').height();//eg 200px/500px
   var handleHeight = Math.round((1-proportion)*$('#scroll-pane').height());//set the proportional height - round it to make sure everything adds up correctly later on
   handleHeight -= handleHeight%2; 

   $("#scroll-pane").after('<\div id="slider-wrap"><\div id="slider-vertical"><\/div><\/div>');//append the necessary divs so they're only there if needed
   $("#slider-wrap").height($("#scroll-pane").height());//set the height of the slider bar to that of the scroll pane


   //set up the slider 
   $('#slider-vertical').slider({
      orientation: 'vertical',
      min: 0,
      max: 100,
      value: 100,
      slide: function(event, ui) {//used so the content scrolls when the slider is dragged
         var topValue = -((100-ui.value)*difference/100);
         $('#updates2').css({top:topValue});//move the top up (negative value) by the percentage the slider has been moved times the difference in height
      },
      change: function(event, ui) {//used so the content scrolls when the slider is changed by a click outside the handle or by the mousewheel
         var topValue = -((100-ui.value)*difference/100);
         $('#updates2').css({top:topValue});//move the top up (negative value) by the percentage the slider has been moved times the difference in height
      }
   });

   //set the handle height and bottom margin so the middle of the handle is in line with the slider
   $(".ui-slider-handle").css({height:handleHeight,'margin-bottom':-0.5*handleHeight});
  
   var origSliderHeight = $("#slider-vertical").height();//read the original slider height
   var sliderHeight = origSliderHeight - handleHeight ;//the height through which the handle can move needs to be the original height minus the handle height
   var sliderMargin =  (origSliderHeight - sliderHeight)*0.5;//so the slider needs to have both top and bottom margins equal to half the difference
   $(".ui-slider").css({height:sliderHeight,'margin-top':sliderMargin});//set the slider height and margins
   
   //create elements to hold the images for the scrollbar handle
   $(".ui-slider-handle").append('<img id="scrollbar-top" src="/images/misc/scrollbar-handle-top.png"/>');
   $(".ui-slider-handle").append('<img id="scrollbar-bottom" src="/images/misc/scrollbar-handle-bottom.png"/>');
   $(".ui-slider-handle").append('<img id="scrollbar-grip" src="/images/misc/scrollbar-handle-grip.png"/>');
}//end if

$(".ui-slider").click(function(event){//stop any clicks on the slider propagating through to the code below
    event.stopPropagation();
   });
   
$("#slider-wrap").click(function(event){//clicks on the wrap outside the slider range
    var offsetTop = $(this).offset().top;//read the offset of the scroll pane
    var clickValue = (event.pageY-offsetTop)*100/$(this).height();//find the click point, subtract the offset, and calculate percentage of the slider clicked
    $("#slider-vertical").slider("value", 100-clickValue);//set the new value of the slider
}); 
   
//additional code for mousewheel
$("#scroll-pane,#slider-wrap").mousewheel(function(event, delta){
  var speed = 5;
  var sliderVal = $("#slider-vertical").slider("value");//read current value of the slider
  
  sliderVal += (delta*speed);//increment the current value

  $("#slider-vertical").slider("value", sliderVal);//and set the new value of the slider
  
  event.preventDefault();//stop any default behaviour
});

});