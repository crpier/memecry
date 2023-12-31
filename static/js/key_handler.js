let currentPostIdx = -1;
/** @type  Element[] */
let availablePosts = [];

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

document.onkeydown = function (e) {
  const { key } = e;
  switch (key) {
    case "j":
      scrollDown(1);
      resetCompositeKeys();
      break;
    case "k":
      scrollUp(1);
      resetCompositeKeys();
      break;
    case "u":
      scrollUp(5);
      resetCompositeKeys();
      break;
    case "d":
      scrollDown(5);
      resetCompositeKeys();
      break;
    case "g":
      switch (compositeKey) {
        case undefined:
          compositeKey = "g";
          break;
        case "g":
          scrollToTop();
          break;
      }

    default:
      break;
  }
};
//
