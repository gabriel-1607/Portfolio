// Global variable 'myurls' is defined in index.html
// Keeps track of data for the paginator
let paginator = {
      current_page: 1,
      max_page: 1,
      url: ''
};

// After the page has been loaded
document.addEventListener('DOMContentLoaded', () => {
      // Many event listeners that call different functions are added
      document.querySelector('#all_posts_button').addEventListener('click', () => {load_posts(myurls.post)});
      document.querySelectorAll('#paginator_button').forEach(button => {
            button.addEventListener('click', () => {paginator_page(button.getAttribute('data-direction'));});
      });
      // Loads posts from the database
      load_posts(myurls.post);
});



// Gets posts from the database via a get request
async function load_posts(url, paginating=false) {

      let json_response;
      try {
            // Makes a fetch request to the server
            const response = await fetch(url);
            // Jsonifies the response
            json_response = await response.json();
      } catch {
            display_message(true, "Failed to load the posts from the server")
      }
      if (json_response.is_error) {
            display_message(true, json_response.message);
            return;
      }

      // Render posts in the DOM
      display_posts(json_response.posts);

      // Update the paginator global variable according to wether the user is
      // paginating across a specific type of posts or is loading a different one from the current one
      if (paginating) {
            reset_paginator(json_response.max_page);
      } else {
            reset_paginator(json_response.max_page, url);
      }
}


// Updates the current page for the paginator
function paginator_page(direction) {

      // Ensures that the paginator does not go beyond the lower and upper limits
      if (direction == "previous" && paginator.current_page > 1) {
            paginator.current_page--;
      }
      else if (direction == "next" && paginator.current_page < paginator.max_page) {
            paginator.current_page++;
      }

      // Loads posts from the database
      load_posts(paginator.url + '?p=' + paginator.current_page, true);
}

// Renders posts in the DOM
function display_posts(posts) {

      // First hides all the posts and then erases all of them
      const all_posts_container = document.querySelector('#posts_container_id');
      all_posts_container.classList.add('d-none');
      all_posts_container.innerHTML = '';

      // Loops through the posts to render each of them in their own box with their separate properties
      posts.forEach(post => {

            // Creates the box for a post
            const post_container = my_create_element(
                  'div',
                  all_posts_container,
                  null,
                  ['border', 'border-3', 'mb-1', 'p-4', 'rounded-2']
            );
            // Creates the header for the post
            my_create_element('h5', post_container, post.user);
            // Adjusts the content of the post to make it include linebreaks
            let post_content = post.content.replace(/^(.+)$/gm, '<p>$1</p>');
            post_content = post_content.replace(/^\n?$/gm, '<br>');
            // Creates the container for the post's content
            my_create_element('div', post_container, post_content, ['mb-3']);
            // Creates the container for the likes number and symbol
            my_create_element('p', post_container, post.likes + document.querySelector('#my_svg').innerHTML);
            // Creates the container for the post's timestamp
            my_create_element('p', post_container, post.timestamp, ['fw-light']);
      });

      // Shows all the posts, that have already been added to the DOM
      all_posts_container.classList.remove('d-none');

      // If the document is larger than the window, show the paginator buttons that are at the bottom of the document
      if (document.documentElement.scrollHeight > window.innerHeight) {
            document.querySelector('#lower-page-navigation').classList.remove('d-none')
      } else {
            document.querySelector('#lower-page-navigation').classList.add('d-none')
      }
}


// Handles the creation of html elements
function my_create_element(my_tag, append_origin, content, my_classes='', my_id='') {
      
      // Creates the element
      const element = document.createElement(`${my_tag}`);
      
      // Adds classes to it, if any
      if (my_classes) {
            element.classList.add(...my_classes);
      }
      
      // Adds an id to it, if any
      if (my_id) {
            element.id = my_id;
      }
      
      // Adds content to it
      element.innerHTML = content;
      
      // Appends it to some other element in the DOM
      append_origin.append(element);
      
      // Returns the created element itself
      return element;
}


// Sets the values of the paginator global variable
function reset_paginator(max_page, url="") {
      paginator.max_page = max_page;
      // When the url of the paginator is updated, also set the current page back to 1
      if (url) {
            paginator.current_page = 1;
            paginator.url = url;
      }
}