/* frontend/static/js/typewriter.js */

function typewrite(element, text, speed = 35) {
  let i = 0;
  if (!element) {
    console.error("typewrite: element not found");
    return;
  }

  function step() {
    element.textContent += text[i];  // ← correct property
    element.scrollTop = element.scrollHeight;
    i++;
    if (i < text.length) {
      setTimeout(step, speed);
    }
  }

  step();
}