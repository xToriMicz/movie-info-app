/**
 * Cloudflare Worker for Movie Info App
 * Proxy requests to Render deployment
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const renderUrl = 'https://movie-info-app.onrender.com'
  
  // Create new request to Render
  const newRequest = new Request(renderUrl + url.pathname + url.search, {
    method: request.method,
    headers: request.headers,
    body: request.body
  })
  
  try {
    // Forward request to Render
    const response = await fetch(newRequest)
    
    // Create new response with CORS headers
    const newResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...Object.fromEntries(response.headers),
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'X-Cloudflare-Worker': 'movie-info-app'
      }
    })
    
    return newResponse
    
  } catch (error) {
    return new Response('Error: ' + error.message, {
      status: 500,
      headers: {
        'Content-Type': 'text/plain',
        'Access-Control-Allow-Origin': '*'
      }
    })
  }
}

// Handle CORS preflight requests
addEventListener('fetch', event => {
  if (event.request.method === 'OPTIONS') {
    event.respondWith(handleCORS(event.request))
  }
})

function handleCORS(request) {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400'
    }
  })
}
