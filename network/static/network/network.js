document.addEventListener('DOMContentLoaded', () => {
      document.querySelector('#post-submit').addEventListener('click', post_compose);
      load_posts();
})

async function load_posts() {
      const response = await fetch('/post');
      const posts = await response.json();

      posts.forEach(post => {
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
            response = await fetch('/post', {
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
      message_element.style.display = 'block';
}