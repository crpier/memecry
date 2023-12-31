let currentPostIdx = -1;
/** @type  Element[] */
let availablePosts = [];
const searchBox = document.getElementById("search");

function inputIsFocused() {
  if (document.activeElement && document.activeElement.tagName == "INPUT") {
    return true;
  }
  return false;
}

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

function handleSimpleKey(key, event) {
  switch (key) {
    case "j":
      scrollDown(1);
      break;
    case "k":
      scrollUp(1);
      break;
    case "u":
      scrollUp(5);
      break;
    case "d":
      scrollDown(5);
      break;
    case "/":
      event.preventDefault();
      // TODO: if there is text in the box already, we should put the cursor at the end
      searchBox.focus();
      resetCompositeKeys();
      break;
    case "g":
      compositeKey = "g";
      break;
    default:
      break;
  }
}

function handleCompositeKey(key) {
  if (compositeKey !== "g") {
    console.error("Composite keys other than g are not supported");
    return;
  }
  switch (key) {
    case "g":
      scrollToTop();
      break;
    case "u":
      window.location.href = "/";
      break;
    default:
      break;
  }
}

function startedCompositeKey(key) {
  if (compositeKey !== undefined) return true;
  return false;
}

document.onkeydown = function (e) {
  const { key } = e;
  // Escape is a special case: we always want the script to handle it
  if (key === "Escape") {
    if (inputIsFocused()) {
      document.activeElement.blur();
    }
    resetCompositeKeys();
    return;
  }
  if (!inputIsFocused()) {
    if (!startedCompositeKey()) {
      handleSimpleKey(key, e);
    } else {
      handleCompositeKey(key);
      resetCompositeKeys();
    }
  }
};
//
