import { resolve } from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        about: resolve(__dirname, 'about-us/index.html'),
        services: resolve(__dirname, 'our-services/index.html'),
        blog: resolve(__dirname, 'blog/index.html'),
        blogPost1: resolve(__dirname, 'blog/seo-is-changing-how-ai-platforms-like-chatgpt-are-redefining-search-visibility/index.html'),
        blogPost2: resolve(__dirname, 'blog/what-is-llm-marketing-a-complete-guide-to-getting-discovered-on-ai-platforms/index.html'),
        blogPost3: resolve(__dirname, 'blog/ai-search-visibility-how-to-show-up-in-chatgpt-perplexity-and-gemini/index.html'),
        contact: resolve(__dirname, 'contact/index.html'),
        digitalStrategy: resolve(__dirname, 'services/digital-strategy-marketing/index.html'),
        thankYou: resolve(__dirname, 'thank-you/index.html')
      }
    }
  }
});
