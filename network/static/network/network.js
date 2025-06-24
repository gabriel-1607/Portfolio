// Global variable 'myurls' is defined in index.html
// Keeps track of a post
let post_id;
// Keeps track of data for the paginator
let paginator = {
      current_page: 1,
      max_page: 1,
      url: ''
};

// After the page has been loaded
document.addEventListener('DOMContentLoaded', () => {

      // Many event listeners that call different functions are added
      document.querySelector('#profile_button').addEventListener('click', () => {load_posts(myurls.profile, undefined, undefined, true);});
      document.querySelector('#all_posts_button').addEventListener('click', () => {load_posts(myurls.post, undefined, true);});
      document.querySelector('#post_submit').addEventListener('click', post_compose);
      document.querySelector('#following_button').addEventListener('click', () => {load_posts(myurls.following, undefined, true);});
      document.querySelector('#save_changes').addEventListener('click', edit_post);
      document.querySelectorAll('#paginator_button').forEach(button => {
            button.addEventListener('click', () => {paginator_page(button.getAttribute('data-direction'));});
      });

      // When the modal for the post is closed, return its values to default
      document.querySelector('#my-modal').addEventListener('hidden.bs.modal', () => {
            document.querySelector('#id_content').value = '';
            document.querySelector('#my-modal-title').innerHTML = 'Your new post';
            document.querySelector('#save_changes').classList.add('d-none');
      });

      // Loads posts from the database
      load_posts(myurls.post);

});



// Gets posts from the database via a get request
// Booleans in function definition are switches to do or not certain actions in this function
async function load_posts(url, paginating=false, hide_users=false, profile=false) {

      // If hide_users parameter is true, hides the containers for the user title and the followed user list
      if (hide_users) {
            document.querySelector('#users_container_id').classList.add('d-none');
            document.querySelector('#users_container_title').classList.add('d-none');
      }

      let json_response;
      try {
            // Makes a fetch request to the server
            const response = await fetch(url);
            // Jsonifies the response
            json_response = await response.json();
      } catch {
            display_message(true, "Failed to properly get the posts from the server");
            return;
      }

      // Render posts in the DOM
      display_posts(json_response.posts);

      // If profile parameter is true, render user info in the DOM
      if (profile) {
            display_users(json_response);
      }

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


// Saves a post to the database via a post request
async function post_compose(event) {

      // Prevents form submission and page reload
      event.preventDefault();

      // Declare the variable to ensure it has scope across the function
      let response;

      // Gets the user input from the textarea
      const content = document.querySelector('#id_content').value;
      // Clears the textarea for the content
      document.querySelector('#id_content').value = "";

      // Disables the submit button while the fetch request is in process
      submit_button = document.querySelector('#post_submit');
      submit_button.disabled = true;

      try {
            // Makes a fetch request to the server, to save the post
            response = await fetch(myurls.post, {
                  method: 'POST',
                  headers: {
                        'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
                  },
                  body: JSON.stringify({
                        content: content
                  })
            });
            // Turns the server response into a json object
            response = await response.json();
      }
      // Handles errors in the fetch request
      catch (error) {
            // Error message
            display_message(true, "Failed to save the post");
            return;
      }

      // Displays custom message from the server
      display_message(response.is_error, response.message);
      load_posts(paginator.url + '?p=' + paginator.current_page, true);

      // Re-enables the submit button
      submit_button.disabled = false;

}


// Updates a post in the database
async function edit_post() {

      // Finds the post's content edited by the user
      const content = document.querySelector('#id_content').value;

      let json_response;
      try {
            // Makes a PUT request to update the post in the database
            const response = await fetch(myurls.edit, {
                  method: 'PUT',
                  headers: {
                        'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
                  },
                  body: JSON.stringify({
                        content: content,
                        id: post_id
                  })
            });

            // Jsonifies the response from the server
            json_response = await response.json();
      } catch {
            display_message(true, "Failed to update the post in the server");
            return;
      }

      // If there has not been an error, load the same page of posts
      if (!json_response.is_error) {
            load_posts(paginator.url + '?p=' + paginator.current_page, true);
      }

      // Render the message from the server response
      display_message(json_response.is_error, json_response.message);
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
            // Creates the container for the likes and the like symbol
            const like_section = my_create_element('p', post_container, "", ['d-flex', 'align-items-center']);
            // Creates the container for the likes number
            const post_likes = my_create_element('span', like_section, post.likes);
            // Creates the like button, in the form of a heart symbol
            const like_button = my_create_element('button', like_section, document.querySelector('#my_svg').innerHTML, ['btn', 'btn-link', 'pb-2'], 'like_button');
            
            // Creates an event listener for the like button
            // It makes a fetch request to the server to update the number of likes for the post
            like_button.addEventListener('click', async () => {

                  let json_response;
                  try {
                        // PUT request to the server, to update likes in the database
                        const response = await fetch(myurls.like, {
                              method: 'PUT',
                              headers: {
                                    'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
                              },
                              body: JSON.stringify({
                                    post_id: post.id
                              })
                        });

                        // Jsonifies the server's response
                        json_response = await response.json();
                  } catch {
                        display_message(true, "Failed to save your like in the server");
                        return;
                  }

                  // Updates the number of likes for the post in the DOM
                  post_likes.innerHTML = json_response.likes;
            });

            // Creates the container for the post's timestamp
            my_create_element('p', post_container, post.timestamp, ['fw-light']);

            // Creates the edit button
            const edit_button = my_create_element('button', post_container, "Edit", ['btn', 'btn-outline-dark', 'btn-sm']);
            // Adds bootstrap attributes to it so that it toggles the modal's display
            edit_button.setAttribute('data-bs-toggle', 'modal');
            edit_button.setAttribute('data-bs-target', '#my-modal');

            // Adds an event listener to the edit button so that it modifies the modal
            edit_button.addEventListener('click', () => {
                  // Changes its title
                  document.querySelector('#my-modal-title').innerHTML = 'Post editor';
                  // Fills it with the post's content
                  document.querySelector('#id_content').value = post.content;
                  // Displays the "save changes" button
                  document.querySelector('#save_changes').classList.remove('d-none');
                  // Updates the global variable post_id to target the current post
                  post_id = post.id;
            });
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


// Renders user information in the DOM
function display_users(json_response) {

      // Hides the user containers and then erases their content
      const users_title = document.querySelector('#users_container_title');
      const all_users_container = document.querySelector('#users_container_id');
      all_users_container.classList.add('d-none');
      users_title.classList.add('d-none');
      all_users_container.innerHTML = '';

      // Creates the container with the number of users followed by the session's user
      my_create_element('p', all_users_container, 'Currently following ' + json_response.following_number + ' users.')
      // Creates the container with the number of followers the user has
      my_create_element('p', all_users_container, 'Currently followed by ' + json_response.followers_number + ' users.')

      // Loops through the user info to create containers for it
      json_response.users.forEach(user => {
            // Creates the container for the user
            const user_container = my_create_element(
                  'li',
                  all_users_container,
                  null,
                  ['list-group-item', 'd-flex', 'align-items-center', 'justify-content-evenly'],       
                  'user_container_id'
            );
            // Creates the container for the user's username
            my_create_element('span', user_container, capitalize_string(user.username));

            // Modifies a string depending on wether the current targeted user is being followed or not by the session's user
            let mystring = 'Follow';
            if (user.is_followed) {
                  mystring = 'Unfollow';
            }
            // Creates a follow button with the above string
            const follow_button = my_create_element('button', user_container, mystring, ['btn', 'btn-primary']);

            // Creates an event listener for the follow button
            // It updates the database to mark users as followed or unfollowed
            follow_button.addEventListener('click', async () => {

                  // Updates the targeted user's status according to its previous status
                  if (user.is_followed) {
                        user.is_followed = false;
                        json_response.following_number--;
                  } else {
                        user.is_followed = true;
                        json_response.following_number++;
                  }

                  // Sends a fetch request to update the user's status in the server
                  try {
                        await fetch(myurls.follow, {
                              method: 'PUT',
                              headers: {
                                    'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
                              },
                              body: JSON.stringify({
                                    user_id: user.id,
                                    start_following: user.is_followed
                              })
                        });
                  } catch {
                        display_message(true, "The server could not process your request to follow the user");
                        return;
                  }

                  // Re-renders all user information in the DOM by calling the parent function again
                  display_users(json_response);
            });
      });

      // Shows both the user title and the container for the users
      all_users_container.classList.remove('d-none');
      users_title.classList.remove('d-none');
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


// Handles the display of custom messages
function display_message(is_error, message) {

      // Find the html element for the message
      message_element = document.querySelector('#id_message');

      // Updates its style class according to the type of message
      if (is_error) {
            message_element.classList.replace('alert-success', 'alert-danger')
      }
      else {
            message_element.classList.replace('alert-danger', 'alert-success')
      }

      // Update its content to become the custom message
      message_element.innerHTML = message;

      // Displays it
      message_element.classList.remove('d-none');
}


// Capitalizes a string
function capitalize_string(mystring) {
      return mystring.charAt(0).toUpperCase() + mystring.slice(1)
}