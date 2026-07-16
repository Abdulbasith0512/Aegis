/// <reference types="vite/client" />

// Allow CSS imports
declare module '*.css' {
  const src: string;
  export default src;
}

// Allow reactflow CSS
declare module 'reactflow/dist/style.css' {
  const src: string;
  export default src;
}
