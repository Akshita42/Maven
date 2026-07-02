import { NextRequest } from "next/server";

const PYTHON_BACKEND_URL = "http://127.0.0.1:8000/api/v1";

async function handleProxy(req: NextRequest, { params }: { params: Promise<{ slug: string[] }> }) {
  const resolvedParams = await params;
  const slug = resolvedParams.slug.join("/");
  const url = new URL(req.url);
  const targetUrl = `${PYTHON_BACKEND_URL}/${slug}${url.search}`;

  const headers = new Headers(req.headers);
  headers.delete("host");

  const options: RequestInit = {
    method: req.method,
    headers,
    redirect: "manual",
  };

  if (req.method !== "GET" && req.method !== "HEAD") {
    options.body = await req.arrayBuffer();
  }

  try {
    const response = await fetch(targetUrl, options);

    // Create a new response to stream back to the client
    const responseHeaders = new Headers(response.headers);
    responseHeaders.delete("content-encoding");

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error("Proxy error:", error);
    return new Response(JSON.stringify({ error: "Failed to connect to AI Microservice" }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }
}

export const GET = handleProxy;
export const POST = handleProxy;
export const PUT = handleProxy;
export const DELETE = handleProxy;
export const PATCH = handleProxy;
export const OPTIONS = handleProxy;
