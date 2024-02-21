import { CONSTANTS } from "./constants.js";

function openSettingsPane() {
  const currentPost = availablePosts[currentPostIdx];
  const settingsPane = currentPost.querySelector(`.${CONSTANTS.POST_SETTINGS_PANE_CLASS}`)
  settingsPane.classList.remove("hidden");
}

function closeSettingsPane() {
  const currentPost = availablePosts[currentPostIdx];
  const settingsPane = currentPost.querySelector(`.${CONSTANTS.POST_SETTINGS_PANE_CLASS}`)
  settingsPane.classList.add("hidden");
}

function openForm(formUrl) {
  htmx.ajax("GET", formUrl, { target: "body", swap: "beforeend" });
}

let currentPostIdx = -1;
/** @type  Element[] */
let availablePosts = [];
const searchBox = document.getElementById("search");

function inputIsFocused() {
  if (
    document.activeElement &&
    (document.activeElement.tagName == "INPUT" ||
      document.activeElement.tagName == "TEXTAREA")
  ) {
    return true;
  }
  return false;
}

function playVideo(event) {
  const currentPost = availablePosts[currentPostIdx];
  const video = currentPost.querySelector("video");
  if (video !== null) {
    if (video.paused) {
      video.play();
    } else {
      video.pause();
    }
  }
}

function increaseVolumeOfVideo(amount) {
  const currentPost = availablePosts[currentPostIdx];
  const video = currentPost.querySelector("video");
  if (video !== null && video.volume < 1) {
    video.volume = Math.floor(video.volume * 10 + amount * 10) / 10;
  }
}

function seekVideoLeft() {
  const currentPost = availablePosts[currentPostIdx];
  const video = currentPost.querySelector("video");
  if (video !== null) {
    video.currentTime -= 1;
  }
}

function seekVideoRight() {
  const currentPost = availablePosts[currentPostIdx];
  const video = currentPost.querySelector("video");
  if (video !== null) {
    video.currentTime += 1;
  }
}
function lowerVolumeOfVideo(amount) {
  const currentPost = availablePosts[currentPostIdx];
  const video = currentPost.querySelector("video");
  if (video !== null && video.volume > 0) {
    // Crazy hack I have to do because if I just do
    // video.volume -= amount
    video.volume = Math.floor(video.volume * 10 - amount * 10) / 10;
  }
}

// Focus the last found input, so that newer elements have priority
function focusInputInForm() {
  const queryResult = document.querySelectorAll("form");
  const form = queryResult[queryResult.length - 1];
  const someInput = form.querySelector("input");
  someInput.focus();
}

function copyLinkToImage() {
  const currentPost = availablePosts[currentPostIdx];
  const result = currentPost.querySelector("img");
  const canvas = document.createElement("canvas");
  if (result !== null) {
    var ctx = canvas.getContext("2d");
    canvas.width = result.width;
    canvas.height = result.height;
    ctx.drawImage(result, 0, 0);
    canvas.toBlob(function (blob) {
      let item;
      try {
        item = new ClipboardItem({ "image/png": blob });
      } catch (e) {
        if (e instanceof ReferenceError) {
          Toastify({
            text: "Copying image not supported in your browser",
            position: "center",
            gravity: "bottom",
            duration: 2000,
            className: "bg-red-600 rounded-md",
            style: {
              background: "rgb(185 28 28)",
            },
          }).showToast();
          return;
        }
      }
      navigator.clipboard.write([item]).then(
        function () {
          Toastify({
            text: "Yanked image",
            position: "center",
            gravity: "bottom",
            duration: 1000,
            className: "bg-green-600 rounded-md",
            style: {
              background: "rgb(22 163 74)",
            },
          }).showToast();
        },
        function (error) {
          console.error("Unable to copy image to clipboard :", error);
        },
      );
    });
  }
}

function copyUrlOfContent() {
  const currentPost = availablePosts[currentPostIdx];
  const result = currentPost.querySelector("[src]");
  const src = result.src;
  navigator.clipboard.writeText(src).then(
    function () {
      Toastify({
        text: `Yanked link ${src}`,
        position: "center",
        gravity: "bottom",
        duration: 2000,
        className: "bg-green-600 rounded-md",
        style: {
          background: "rgb(22 163 74)",
        },
      }).showToast();
    },
    function (error) {
      console.error("Unable to copy link to clipboard :", error);
    },
  );
}

function scrollDown(count) {
  try {
    const newPostIdx = Math.min(
      currentPostIdx + count,
      availablePosts.length - 1,
    );
    if (currentPostIdx === newPostIdx) {
      return;
    }
    currentPostIdx += count;
    availablePosts[newPostIdx].scrollIntoView({ behavior: "instant" });
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
    const newPostIdx = Math.max(currentPostIdx - count, 0);
    if (currentPostIdx === newPostIdx) {
      return;
    }
    availablePosts[newPostIdx].scrollIntoView({ behavior: "instant" });
  } catch (e) {
    console.log(e);
    if (e instanceof TypeError) {
      currentPostIdx--;
    } else {
      throw e;
    }
  }
}

function scrollToTop() {
  currentPostIdx = 0;
  availablePosts[currentPostIdx].scrollIntoView({ behavior: "instant" });
}

function scrollToBottom() {
  currentPostIdx = availablePosts.length - 1;
  availablePosts[currentPostIdx].scrollIntoView({ behavior: "instant" });
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

  if (availablePosts[currentPostIdx] !== undefined) {
    availablePosts[currentPostIdx].focus();
    // TODO: allow config option for user to autoplay video
    // const video = availablePosts[currentPostIdx].querySelector("video");
    // if (video !== null) {
    //   if (video.paused) {
    //     video.play();
    //   }
    // }
  }
}

function reloadAvailablePosts() {
  availablePosts = [];
  const elements = document.getElementsByClassName(
    CONSTANTS.POST_COMPONENT_CLASS,
  );
  for (let i = 0; i < elements.length; i++) {
    availablePosts.push(elements[i]);
    if (elements[i].onblur === null) {
      elements[i].onblur = function (event) {
        const video = event.target.querySelector("video");
        if (video !== null) {
          if (!video.paused) {
            video.pause();
          }
        }
      };
    }
  }
}

htmx.on("htmx:afterSettle", function (_) {
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

// TODO buttons to log out, control video volume, close the window
function handleSimpleKey(key, event) {
  switch (key) {
    case "i":
      openForm("/signin-form");
      break;
    case "a":
      openForm("/upload-form");
      break;
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
    case "y":
      copyLinkToImage();
      break;
    case "G":
      scrollToBottom();
      break;
    case "Q":
      openForm("/signout");
      break;
    case "ArrowLeft":
      event.preventDefault();
      seekVideoLeft();
      break;
    case "ArrowRight":
      event.preventDefault();
      seekVideoRight();
      break;
    case " ":
      event.preventDefault();
      playVideo(event);
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
    case "z":
      compositeKey = "z";
      break;
    case "<":
      lowerVolumeOfVideo(0.2);
      break;
    case ">":
      // TODO: allow changing the default volume of videos
      increaseVolumeOfVideo(0.2);
      break;
    default:
      break;
  }
}

function handleCompositeKey(key, event) {
  if (compositeKey === "g") {
    switch (key) {
      case "g":
        scrollToTop();
        break;
      case "u":
        window.location.href = "/";
        break;
      case "y":
        copyUrlOfContent();
        break;
      case "i":
        event.preventDefault();
        focusInputInForm();
        break;
      default:
        break;
    }
  } else if (compositeKey === "z") {
    switch (key) {
      case "a":
        openSettingsPane();
        break;
      case "c":
        closeSettingsPane();
        break;
      default:
        break;
    }
  } else {
    console.error('Composite keys other than "g" and "z" are not supported');
  }
}

function startedCompositeKey() {
  if (compositeKey !== undefined) return true;
  return false;
}

// TODO: buttons for signin/signout
document.onkeydown = function (e) {
  const { key } = e;
  // Escape is a special case: we always want the script to handle it
  if (key === "Escape") {
    if (inputIsFocused()) {
      document.activeElement.blur();
      return;
    }
    resetCompositeKeys();
    return;
  }
  if (!inputIsFocused()) {
    if (!startedCompositeKey()) {
      handleSimpleKey(key, e);
    } else {
      handleCompositeKey(key, e);
      resetCompositeKeys();
    }
  }
};
// TODO: there is a bug where after using d/u we sometimes stop scrolling behavior
// TODO: aargh, when posts are too tall, scrolling doesn't show the title; guess we'll have to
// scroll to the top of the post, in the end
