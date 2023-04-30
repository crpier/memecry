from typing import Callable
from lib.html import CleanHTML, component, html
from src.schema import User


@component
def html_root(child: Callable[[], CleanHTML]):
    __import__('pdb').set_trace()
    return (
        html
        @ f"""
          <!DOCTYPE html>
          <html lang="en">
              <head>
                  <meta charset="UTF-8">
                  <title>Memecry</title>
                  <link rel="icon" href="static/favicon.ico" type="image/xicon" />
                  <link href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css"
                        rel="stylesheet" />
                  <script src="/static/js/htmx.min.js?v=1.5.0"></script>
                  <link rel="stylesheet"
                        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
              </head>
              <body class="bg-black text-white h-screen">{child()}</body>
        """
    )


@component
def nav(user: User | None):
    signup_button = (
        html
        @ """
          <button class="mr-4 inline-block rounded border border-white px-4 py-2 text-sm leading-none hover:border-transparent hover:bg-white hover:text-teal-500"
                  hx-get="/signup-form"
                  hx-target="#signup-modal"
                  hx-trigger="click">Sign Up</button>
        """
    )
    signin_button = (
        html
        @ """
          <button class="mr-4 inline-block rounded border border-white px-4 py-2 text-sm leading-none hover:border-transparent hover:bg-white hover:text-teal-500"
                  hx-get="/login-form"
                  hx-target="#login-modal"
                  hx-trigger="click">Sign in</button>
    """
    )
    upload_button = (
        html
        @ """
          <button hx-get="/upload-form"
                  hx-target="#upload-modal"
                  hx-trigger="click"
                  class="mr-4 inline-block rounded border-white bg-blue-500 px-4 py-2 text-sm font-semibold leading-none hover:border-transparent hover:bg-white hover:text-teal-500 ">
              Upload
          </button>
    """
    )
    user_links = (
        html
        @ """
          <a href="#responsive-header"
             class="flex flex-row items-center pr-2 hover:bg-gray-800 hover:text-white">
              <button class="h-12 w-12">
                  <img alt="profile-picture" class="m-auto w-8 h-8 rounded-lg" src={{"https://avatars.githubusercontent.com/u/31815875?v=4" }} />
              </button>
              <span>{{ user.username }}</span>
          </a>
    """
    )
    logout_button = (
        html
        @ """
          <button class="inline-block rounded rounded border border-white px-4 py-2 leading-none hover:border-transparent hover:bg-white hover:text-teal-500 "
                  hx-post="/logout"
                  hx-trigger="click">Sign Out</button>
    """
    )
    return (
        html
        @ f"""
          <nav class="flex flex-row items-center bg-gray-900 p-3 fixed w-full h-14">
              <a href="/" class="mr-6 flex flex-shrink-0 items-center">
                  <span class="text-xl font-semibold tracking-tight">Memecry</span>
              </a>
              <a href="/new"
                 class="mr-4 block hover:text-gray-300 lg:mt-0 lg:inline-block">New</a>
              <div class="lg:flex-grow"></div>
              <button class="">
                  <i class="fa fa-search fa-lg h-6 mr-4"></i>
              </button>
              {signup_button if not user else ""}
              {signin_button if not user else ""}
              {upload_button if user else ""}
              {user_links if user else ""}
              {logout_button if user else ""}
          </nav>
        """
    )
