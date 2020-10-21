// Code adapted from: https://www.w3schools.com/howto/howto_js_draggable.asp

function makeElementDraggable(elmnt) {
  let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  elmnt.onmousedown = dragMouseDown;
  elmnt.ontouchstart = dragMouseDown

  function dragMouseDown(e) {
    // strictly enforce the drag handler
    // only applying to the specified element,
    // thereby preventing a child DOM element click
    // from initiating a drag of the parent element.
    if (e.target == elmnt) {
      e = e || window.event;
      e.preventDefault();
      // get the mouse cursor position at startup:
      if (e.type === "touchstart") {
        pos3 = e.touches[0].clientX;
        pos4 = e.touches[0].clientY;
      } else {
        pos3 = e.clientX;
        pos4 = e.clientY;
      }
      // call a function whenever the cursor moves:
      document.addEventListener('mouseup', closeDragElement, {passive: false});
      document.addEventListener('touchend', closeDragElement, {passive: false});
      document.addEventListener('mousemove', elementDrag, {passive: false});
      document.addEventListener('touchmove', elementDrag, {passive: false});
    }
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    // calculate the new cursor position:
    if (e.type === "touchmove") {
      pos1 = pos3 - e.touches[0].clientX;
      pos2 = pos4 - e.touches[0].clientY;
      pos3 = e.touches[0].clientX;
      pos4 = e.touches[0].clientY;
    } else {
      pos1 = pos3 - e.clientX;
      pos2 = pos4 - e.clientY;
      pos3 = e.clientX;
      pos4 = e.clientY;
    }
    // set the element's new position:
    elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
    elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
  }

  function closeDragElement() {
    // stop moving when mouse button is released:
    document.removeEventListener('mouseup', closeDragElement, {passive: false});
    document.removeEventListener('touchend', closeDragElement, {passive: false});
    document.removeEventListener('mousemove', elementDrag, {passive: false});
    document.removeEventListener('touchmove', elementDrag, {passive: false});
  }
}