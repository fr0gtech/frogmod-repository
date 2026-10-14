# Frogtech Mod Loader repository template

Ship your Deadlock mods through [Frogtech Mod Loader](https://mods.frogtech.dev/mod-loader): players add your
repository once, install your mods with one click, and get every update automatically.

This template hosts the repository for free on GitHub: you list your mods in `mods.json`, upload each version as a
release, and a GitHub Action builds `repo.json` (with checksums) and publishes it on GitHub Pages.

## Set it up (5 minutes)

1. Press **Use this template** (top right) and create your repository. Public is easiest.
2. In your new repository: **Settings, Pages**, set **Source** to **GitHub Actions**.
3. Edit `mods.json`: your repository's name and description, and one entry per mod (`id`, `name`, and optionally
   `description`, `tags`, `image`, `page`, `notes`). The `id` never changes: a-z, 0-9, `_` and `-`.
4. Make a release (**Releases, Draft a new release**) and attach your mod as `<id>_v<version>.zip`,
   for example `example_hud_v1.0.zip`. The zip holds your `pak01_dir.vpk` (or several `*_dir.vpk`); a bare `.vpk`
   named `<id>_v<version>.vpk` works too.
5. Publishing the release runs the Action. Your repository is then at
   `https://<your-name>.github.io/<your-repo>/repo.json`.

Players add that address in the loader (**Settings, Repositories, Add**), or with one click from your page:

```
frogmod://repo/add?url=https%3A%2F%2F<your-name>.github.io%2F<your-repo>%2Frepo.json
```

## Shipping an update

Make a new release with the higher version in the file name (`example_hud_v1.1.zip`). The Action picks the newest
version of each mod, and players get it the next time their loader checks (within the hour).

Keep old releases: they're your download history, and the file names tell the Action what's newest.

## The format

The full description, including every field, is at **https://mods.frogtech.dev/docs/repositories**.
`schema/repository.schema.json` is the JSON Schema; the Action checks `repo.json` against it before publishing.

Short version:

```json
{
  "format": 1,
  "name": "My Deadlock Mods",
  "mods": [
    { "id": "example_hud", "name": "Example HUD", "version": "1.1",
      "url": "https://github.com/me/my-mods/releases/download/v1.1/example_hud_v1.1.zip",
      "sha256": "…", "size": 48213, "tags": ["HUD"] }
  ]
}
```

`format`, `name` and `mods` are required, and each mod needs `id`, `name`, `version`, `url` and `sha256`. This
template fills in `version`, `url`, `size` and `sha256` for you.

## Paid or private mods

GitHub Pages is public, so this template is for free mods. For paid or private mods, serve `repo.json` from your
own server: players enter a key when adding your repository, and the loader sends it as
`Authorization: Bearer <key>` to your repository's address (and to downloads on the same address only). Your server
can then list only the mods each key owns. See the docs above.

## Build it yourself

```
GITHUB_REPOSITORY=<you>/<repo> python3 scripts/build_repo.py   # writes site/repo.json
```

## License

MIT. Do whatever you like with this template.
