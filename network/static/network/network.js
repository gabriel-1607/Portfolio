// Global variable 'myurls' is defined in index.html

document.addEventListener('DOMContentLoaded', () => {
      document.querySelector('#profile_button').addEventListener('click', load_profile);
      document.querySelector('#all_posts_button').addEventListener('click', () => {load_posts(myurls.post)});
      document.querySelector('#post-submit').addEventListener('click', post_compose);
      document.querySelector('#following_button').addEventListener('click', () => {load_posts(myurls.following)});
      load_posts(myurls.post);
})



// Loads and displays info about the user: the posts, the number of followers and of users followed,
// plus a list of all the other users, with a button to toggle their followed or not followed status
async function load_profile() {

      const all_posts_container = document.querySelector('#posts_container_id');
      const users_title = document.querySelector('#users_container_title');
      const all_users_container = document.querySelector('#users_container_id');

      const response = await fetch(myurls.profile);
      const json_response = await response.json();

      all_posts_container.classList.add('d-none');
      all_users_container.classList.add('d-none');
      users_title.classList.add('d-none');
      all_users_container.innerHTML = '';
      all_posts_container.innerHTML = '';

      display_posts(json_response.posts);
      display_users(json_response);
      
      all_posts_container.classList.remove('d-none');
      all_users_container.classList.remove('d-none');
      users_title.classList.remove('d-none');
}


// Gets posts from the database via a get request
async function load_posts(url) {

      const all_posts_container = document.querySelector('#posts_container_id');

      
      document.querySelector('#users_container_id').classList.add('d-none');
      document.querySelector('#users_container_title').classList.add('d-none');



      const response = await fetch(url);
      const json_response = await response.json();


      all_posts_container.classList.add('d-none');
      all_posts_container.innerHTML = '';
      display_posts(json_response.posts);
      all_posts_container.classList.remove('d-none');
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
      submit_button = document.querySelector('#post-submit');
      submit_button.disabled = true;

      try {
            // Makes a fetch request to the server, to save the post
            response = await fetch(myurls.post, {
                  method: 'POST',
                  headers: {
                        'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
                  },
                  body: JSON.stringify({
                        content: content,
                        user: document.querySelector('#id_user').value
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


function display_posts(posts) {

      posts.forEach(post => {
            // TODO : probably the specific id is unnecessary and I should replace it with null
            const post_container = my_create_element(
                  'div',
                  document.querySelector('#posts_container_id'),
                  null,
                  ['border', 'border-3', 'mb-1', 'p-4', 'rounded-2'],
                  `post_${post.id}`
            );
            my_create_element('h5', post_container, post.user);
            my_create_element('div', post_container, post.content,
                  ['mb-3']
            );
            my_create_element('p', post_container, document.querySelector('#my_svg').innerHTML + post.likes)
            my_create_element('p', post_container, post.timestamp, ['fw-light']);
      });

}


function display_users(json_response) {

      const all_users_container = document.querySelector('#users_container_id');

      my_create_element('p', all_users_container, 'Currently following ' + json_response.following_number + ' users.')
      my_create_element('p', all_users_container, 'Currently followed by ' + json_response.followers_number + ' users.')
      json_response.users.forEach(user => {
            const user_container = my_create_element(
                  'li',
                  all_users_container,
                  null,
                  ['list-group-item', 'd-flex', 'align-items-center', 'justify-content-evenly'],       
                  'user_container_id'
            )
            my_create_element('span', user_container, capitalize_string(user.username))

            let mystring = 'Follow';
            if (user.is_followed) {
                  mystring = 'Unfollow';
            }

            const follow_button = my_create_element('button', user_container, mystring, ['btn', 'btn-primary'])
            follow_button.addEventListener('click', async () => {

                  if (user.is_followed) {
                        user.is_followed = false;
                        json_response.following_number--;
                  } else {
                        user.is_followed = true;
                        json_response.following_number++;
                  }

                  all_users_container.classList.add('d-none');
                  all_users_container.innerHTML = '';

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

                  all_users_container.classList.remove('d-none');
            })
      })
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