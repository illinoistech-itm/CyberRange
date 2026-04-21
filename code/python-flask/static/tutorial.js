function openTutorial() {
  document.getElementById('tutorial-overlay').classList.add('active');
}

function closeTutorial() {
  document.getElementById('tutorial-overlay').classList.remove('active');
  localStorage.setItem('cyberrange_tutorial_seen', '1');
}

function switchTab(os, btn) {
  document.querySelectorAll('.tutorial-tab-content').forEach(function(el) {
    el.style.display = 'none';
  });
  document.querySelectorAll('.tutorial-tab').forEach(function(el) {
    el.classList.remove('active');
  });
  document.getElementById('tutorial-' + os).style.display = 'block';
  btn.classList.add('active');
}

document.addEventListener('DOMContentLoaded', function() {
  // Close when clicking the dark backdrop
  var overlay = document.getElementById('tutorial-overlay');
  if (overlay) {
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) closeTutorial();
    });
  }

  // Close on Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeTutorial();
  });
});
