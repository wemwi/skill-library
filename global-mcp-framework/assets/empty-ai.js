// empty-ai.js — leerer Stub für den `ai`-Alias aus wrangler.jsonc.
//
// Eine Dependency im Baum (über die Foundation) referenziert das `ai`-Modul, das
// dieser Worker nicht nutzt. Der Alias `"ai": "./src/empty-ai.js"` in der
// wrangler.jsonc biegt diesen Import auf diesen leeren Default-Export um, damit das
// Bundling nicht an einem fehlenden Modul scheitert.
//
// Ablage im Repo: src/empty-ai.js (nicht in assets/ — das hier ist nur der Spiegel).
export default {};
