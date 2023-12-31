let currentPostIdx = -1;
/** @type  Element[] */
let availablePosts = [];
const searchBox = document.getElementById("search");

function scrollDown(count) {
  try {
    currentPostIdx += count;
    availablePosts[currentPostIdx].scrollIntoView({
      block: "center",
      behavior: "smooth",
    });
  } catch (e) {
    if (e instanceof TypeError) {
      currentPostIdx--;
    } else {
      throw e;
    }
  }
}

function scrollUp(count) {
  try {
    currentPostIdx -= count;
    availablePosts[currentPostIdx].scrollIntoView({
      block: "center",
      behavior: "smooth",
    });
  } catch (e) {
    if (e instanceof TypeError) {
      currentPostIdx--;
    } else {
      throw e;
    }
  }
}

function scrollToTop() {
  currentPostIdx = 0;
  availablePosts[currentPostIdx].scrollIntoView({
    block: "center",
    behavior: "smooth",
  });
}

function updateCurrentPostIdx() {
  let newIdx;
  for (let i = 0; i < availablePosts.length; i++) {
    const rect = availablePosts[i].getBoundingClientRect();
    const inView = rect.top >= 0;
    if (inView) {
      newIdx = i;
      break;
    }
  }
  if (newIdx !== undefined && newIdx !== currentPostIdx) {
    currentPostIdx = newIdx;
  }
}

function reloadAvailablePosts() {
  availablePosts = [];
  const elements = document.getElementsByClassName("post-component");
  for (let i = 0; i < elements.length; i++) {
    availablePosts.push(elements[i]);
  }
}

htmx.on("htmx:afterSettle", function (e) {
  reloadAvailablePosts();
});

setTimeout(() => {
  reloadAvailablePosts();
  updateCurrentPostIdx();
});

document.onscroll = function () {
  updateCurrentPostIdx();
};

let compositeKey;

function resetCompositeKeys() {
  compositeKey = undefined;
}

function inputIsFocused() {
  if (document.activeElement && document.activeElement.tagName == "INPUT") {
    return true
  }
  return false;
}

document.onkeydown = function (e) {
  const { key } = e;
  switch (key) {
    case "j":
      if (!inputIsFocused()) {
        scrollDown(1);
        resetCompositeKeys();
      }
      break;
    case "k":
      if (!inputIsFocused()) {
        scrollUp(1);
        resetCompositeKeys();
      }
      break;
    case "u":
      if (!inputIsFocused()) {
        scrollUp(5);
        resetCompositeKeys();
      }
      break;
    case "d":
      if (!inputIsFocused()) {
        scrollDown(5);
        resetCompositeKeys();
      }
      break;
    case "/":
      if (!inputIsFocused()) {
        e.preventDefault();
        // TODO: if there is text in the box already, we should put the cursor at the end
        searchBox.focus();
      }
      resetCompositeKeys();
      break;
    case "Escape":
      if (inputIsFocused()) {
        document.activeElement.blur();
      }
      resetCompositeKeys();
      break;
    case "g":
      if (!inputIsFocused()) {
        switch (compositeKey) {
          case undefined:
            compositeKey = "g";
            break;
          case "g":
            scrollToTop();
            break;
        }
      }

    default:
      break;
  }
};
//
