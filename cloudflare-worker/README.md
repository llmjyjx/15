# Cloudflare Worker API

```bash
npm install -g wrangler
wrangler login
wrangler d1 create xiangpan-art
wrangler r2 bucket create xiangpan-art
wrangler d1 execute xiangpan-art --remote --file=schema.sql
wrangler d1 execute xiangpan-art --remote --file=../migration/art.sql
wrangler deploy
```

部署前修改 `wrangler.toml` 和前端 `api.js`。
