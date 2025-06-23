// Global variable 'myurls' is defined in index.html
let post_id;
let paginator = {
      current_page: 1,
      max_page: 1,
      url: ''
};

document.addEventListener('DOMContentLoaded', () => {
      document.querySelector('#profile_button').addEventListener('click', () => {load_posts(myurls.profile, undefined, undefined, true);});
      document.querySelector('#all_posts_button').addEventListener('click', () => {load_posts(myurls.post, undefined, true);});
      document.querySelector('#post_submit').addEventListener('click', post_compose);
      document.querySelector('#following_button').addEventListener('click', () => {load_posts(myurls.following, undefined, true);});
      document.querySelector('#save_changes').addEventListener('click', edit_post);
      document.querySelectorAll('#paginator_button').forEach(button => {
            button.addEventListener('click', () => {paginator_page(button.getAttribute('data-direction'));});
      });
      document.querySelector('#my-modal').addEventListener('hidden.bs.modal', () => {
            document.querySelector('#id_content').value = '';
            document.querySelector('#my-modal-title').innerHTML = 'Your new post';
            document.querySelector('#save_changes').classList.add('d-none');
      });
      load_posts(myurls.post);
});



// Gets posts from the database via a get request
async function load_posts(url, paginating=false, hide_users=false, profile=false) {

      if (hide_users) {
            document.querySelector('#users_container_id').classList.add('d-none');
            document.querySelector('#users_container_title').classList.add('d-none');
      }

      const response = await fetch(url);
      const json_response = await response.json();

      display_posts(json_response.posts);

      if (profile) {
            display_users(json_response);
      }

      if (paginating) {
            reset_paginator(json_response.max_page);
      } else {
            reset_paginator(json_response.max_page, url);
      }
}


function paginator_page(direction) {
      if (direction == "previous" && paginator.current_page > 1) {
            paginator.current_page--;
      }
      else if (direction == "next" && paginator.current_page < paginator.max_page) {
            paginator.current_page++;
      }
      load_posts(paginator.url + '?p=' + paginator.current_page, true);
}


// TODO: load the posts again after saving a new post.
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

      // Re-enables the submit button
      submit_button.disabled = false;

}


// TODO: Need the post_id to be able to target the post to be edited in the database
async function edit_post() {
      const content = document.querySelector('#id_content').value;
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
      const json_response = await response.json();

      if (!json_response.is_error) {
            load_posts(paginator.url + '?p=' + paginator.current_page, true);
      }
      display_message(json_response.is_error, json_response.message);
}


// TODO: Linebreaks should be properly displayed in the posts
function display_posts(posts) {

      const all_posts_container = document.querySelector('#posts_container_id');
      all_posts_container.classList.add('d-none');
      all_posts_container.innerHTML = '';

      posts.forEach(post => {
            // TODO : probably the specific id is unnecessary and I should replace it with null
            const post_container = my_create_element(
                  'div',
                  all_posts_container,
                  null,
                  ['border', 'border-3', 'mb-1', 'p-4', 'rounded-2'],
                  `post_${post.id}`
            );
            my_create_element('h5', post_container, post.user);
            my_create_element('div', post_container, post.content, ['mb-3']);
            const like_section = my_create_element('p', post_container, "", ['d-flex', 'align-items-center']);
            const post_likes = my_create_element('span', like_section, post.likes);
            const like_button = my_create_element('button', like_section, document.querySelector('#my_svg').innerHTML, ['btn', 'btn-link', 'pb-2'], 'like_button');
            like_button.setAttribute('data-post-id', `${post.id}`);
            like_button.addEventListener('click', async () => {
                  const response = await fetch(myurls.like, {
                        method: 'PUT',
                        headers: {
                              'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
                        },
                        body: JSON.stringify({
                              post_id: post.id
                        })
                  });
                  const json_response = await response.json();
                  post_likes.innerHTML = json_response.likes;
            });
            my_create_element('p', post_container, post.timestamp, ['fw-light']);
            const edit_button = my_create_element('button', post_container, "Edit", ['btn', 'btn-outline-dark', 'btn-sm']);
            edit_button.setAttribute('data-bs-toggle', 'modal');
            edit_button.setAttribute('data-bs-target', '#my-modal');
            edit_button.addEventListener('click', () => {
                  document.querySelector('#my-modal-title').innerHTML = 'Post editor';
                  document.querySelector('#id_content').value = post.content;
                  document.querySelector('#save_changes').classList.remove('d-none');
                  post_id = post.id;
            });
      });

      all_posts_container.classList.remove('d-none');

}


function display_users(json_response) {

      const users_title = document.querySelector('#users_container_title');
      const all_users_container = document.querySelector('#users_container_id');
      all_users_container.classList.add('d-none');
      users_title.classList.add('d-none');
      all_users_container.innerHTML = '';

      my_create_element('p', all_users_container, 'Currently following ' + json_response.following_number + ' users.')
      my_create_element('p', all_users_container, 'Currently followed by ' + json_response.followers_number + ' users.')
      json_response.users.forEach(user => {
            const user_container = my_create_element(
                  'li',
                  all_users_container,
                  null,
                  ['list-group-item', 'd-flex', 'align-items-center', 'justify-content-evenly'],       
                  'user_container_id'
            );
            my_create_element('span', user_container, capitalize_string(user.username));

            let mystring = 'Follow';
            if (user.is_followed) {
                  mystring = 'Unfollow';
            }

            const follow_button = my_create_element('button', user_container, mystring, ['btn', 'btn-primary']);
            follow_button.addEventListener('click', async () => {

                  if (user.is_followed) {
                        user.is_followed = false;
                        json_response.following_number--;
                  } else {
                        user.is_followed = true;
                        json_response.following_number++;
                  }

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

                  display_users(json_response);

            });
      });

      all_users_container.classList.remove('d-none');
      users_title.classList.remove('d-none');
}


function reset_paginator(max_page, url="") {
      paginator.max_page = max_page;
      paginator.current_page = 1;
      if (url) {
            paginator.url = url;
      }
}


// Handles the creation of html elements
function my_create_element(my_tag, append_origin, content, my_classes='', my_id='') {
      const element = document.createElement(`${my_tag}`);
      if (my_classes) {
            element.classList.add(...my_classes);
      }
      if (my_id) {
            element.id = my_id;
      }
      element.innerHTML = content;
      append_origin.append(element);
      return element;
}


// TODO: Switch to BS toasts and erase the div currently being used for message display
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