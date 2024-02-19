import { CONSTANTS } from "./constants.js";

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
    event.preventDefault();
    if (video.paused) {
      video.play();
    } else {
      video.pause();
    }
  }
}

function login() {
  // TODO: get id from constant
  const el = document.getElementById("signin");
  el.click();
}

function focusInputInForm() {
  const form = document.querySelectorAll("form")[1];
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
    canvas.toBlob(function(blob) {
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
        function() {
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
        function(error) {
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
    function() {
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
    function(error) {
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
  // TODO: if we need to scroll 5 posts, but there are 3 left, we should scroll 3
  // right now, we don't scroll at all
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
      elements[i].onblur = function(event) {
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

htmx.on("htmx:afterSettle", function(_) {
  reloadAvailablePosts();
});

setTimeout(() => {
  reloadAvailablePosts();
  updateCurrentPostIdx();
});

document.onscroll = function() {
  updateCurrentPostIdx();
};

let compositeKey;

function resetCompositeKeys() {
  compositeKey = undefined;
}

// TODO: G key should take us to the last post
// TODO buttons to log out, control video volume
function handleSimpleKey(key, event) {
  switch (key) {
    case "i":
      login();
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
    case " ":
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
    default:
      break;
  }
}

function handleCompositeKey(key, event) {
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
}

function startedCompositeKey(_) {
  if (compositeKey !== undefined) return true;
  return false;
}

// TODO: buttons for signin/signout
document.onkeydown = function(e) {
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
