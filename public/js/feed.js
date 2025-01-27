const newPostForm = document.getElementById('new-post-form');
const postContentInput = document.getElementById('post-content');
const feedPosts = document.getElementById('feed-posts');

async function fetchPosts() {
  const response = await fetch('/api/posts');
  const posts = (await response.json())?.posts;

  feedPosts.innerHTML = '';
  posts.forEach((post) => {
    const postElement = document.createElement('div');
    postElement.className = 'border border-gray-300 rounded-lg p-4 shadow-md';

    postElement.innerHTML = `
          <h2 class="text-lg font-semibold">${post.title}</h2>
          <p class="text-sm text-gray-500 mb-4">By ${post.author}</p>
          <p>${post.content}</p>

          <div class="mt-4 flex items-center justify-between">
            <button onclick='likePost("${post.id}")' class="like-btn bg-blue-600 px-2 py-1 rounded-md">
              👍 ${post.likes.length} Likes
            </button>
            <p id='like-list' class="text-sm text-gray-500">People who liked: ${post.likes.join(", ")}</p>
          </div>
        `;

    feedPosts.appendChild(postElement);
  });
}

fetchPosts();

async function likePost(postId) {
  await fetch(`/api/posts/${postId}/like`, {
    method: 'POST',
  });
  fetchPosts();
}