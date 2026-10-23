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
        blogPost3: resolve(__dirname, 'blog/ai-search-visibility-how-to-show-up-in-chatgpt-perplexity-and-gemini/index.html'),
        blogPost4: resolve(__dirname, 'blog/how-to-get-your-brand-recommended-by-chatgpt/index.html'),
        blogPost5: resolve(__dirname, 'blog/geo-vs-seo/index.html'),
        blogPost8: resolve(__dirname, 'blog/ai-advertising/index.html'),
        blogPost7: resolve(__dirname, 'blog/what-is-llm-marketing/index.html'),
        blogPost6: resolve(__dirname, 'blog/schema-entity-optimization-llms/index.html'),
        authorAdil: resolve(__dirname, 'author/mohd-adil-kazmi/index.html'),
        ServicesAiSearchVisibility: resolve(__dirname, 'services/ai-search-visibility/index.html'),
        ServicesAiSeo: resolve(__dirname, 'services/ai-seo/index.html'),
        ServicesAiLeadAgents: resolve(__dirname, 'services/ai-lead-agents/index.html'),
        ServicesMarketingAutomation: resolve(__dirname, 'services/marketing-automation/index.html'),
        ServicesEmailMarketing: resolve(__dirname, 'services/email-marketing/index.html'),
        CaseStudies: resolve(__dirname, 'case-studies/index.html'),
        OurApproach: resolve(__dirname, 'our-approach/index.html'),
        BookACall: resolve(__dirname, 'book-a-call/index.html'),
        PrivacyPolicy: resolve(__dirname, 'privacy-policy/index.html'),
        contact: resolve(__dirname, 'contact/index.html'),
        digitalStrategy: resolve(__dirname, 'services/digital-strategy-marketing/index.html'),
        thankYou: resolve(__dirname, 'thank-you/index.html')
      }
    }
  }
});
