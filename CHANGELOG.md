# Changelog

## [1.2.5](https://github.com/alrayyes/hush-hush-python/compare/v1.2.4...v1.2.5) (2026-09-03)


### Bug Fixes

* **ci:** remove codegen's leftover auto-merge step ([#38](https://github.com/alrayyes/hush-hush-python/issues/38)) ([8b361ef](https://github.com/alrayyes/hush-hush-python/commit/8b361ef64f515c48f10f147b45ee5c1eb9b3ac72))

## [1.2.4](https://github.com/alrayyes/hush-hush-python/compare/v1.2.3...v1.2.4) (2026-09-02)


### Bug Fixes

* **ci:** use RELEASE_TOKEN for the codegen PR, not GITHUB_TOKEN ([#34](https://github.com/alrayyes/hush-hush-python/issues/34)) ([e80f6ce](https://github.com/alrayyes/hush-hush-python/commit/e80f6cedc6c6aa910b6d19286f9fd3d5be6b3018)), closes [#33](https://github.com/alrayyes/hush-hush-python/issues/33)

## [1.2.3](https://github.com/alrayyes/hush-hush-python/compare/v1.2.2...v1.2.3) (2026-09-02)


### Bug Fixes

* pin gh-action-pypi-publish to its commit SHA, not the tag object SHA ([#30](https://github.com/alrayyes/hush-hush-python/issues/30)) ([ad563f8](https://github.com/alrayyes/hush-hush-python/commit/ad563f8ed59a741f9d506a40324bb48f7a51d6d2))

## [1.2.2](https://github.com/alrayyes/hush-hush-python/compare/v1.2.1...v1.2.2) (2026-09-02)


### Bug Fixes

* correct release-please output keys for the publish job ([#28](https://github.com/alrayyes/hush-hush-python/issues/28)) ([614cd30](https://github.com/alrayyes/hush-hush-python/commit/614cd3007f28806081f09787162eb1fd7a314dc6))

## [1.2.1](https://github.com/alrayyes/hush-hush-python/compare/v1.2.0...v1.2.1) (2026-09-02)


### Documentation

* add GitHub issue and PR templates ([#26](https://github.com/alrayyes/hush-hush-python/issues/26)) ([51c35d0](https://github.com/alrayyes/hush-hush-python/commit/51c35d063c7dfab9dc7984656186bd790a8bea98))

## [1.2.0](https://github.com/alrayyes/hush-hush-python/compare/v1.1.2...v1.2.0) (2026-09-02)


### Features

* publish releases to PyPI via Trusted Publishing ([#22](https://github.com/alrayyes/hush-hush-python/issues/22)) ([0ccfe09](https://github.com/alrayyes/hush-hush-python/commit/0ccfe09588d4feac6065cb073ebb02c0836a8101)), closes [#21](https://github.com/alrayyes/hush-hush-python/issues/21)

## [1.1.2](https://github.com/alrayyes/hush-hush-python/compare/v1.1.1...v1.1.2) (2026-09-02)


### Bug Fixes

* regenerate client from updated hush-hush spec ([#17](https://github.com/alrayyes/hush-hush-python/issues/17)) ([5d1269d](https://github.com/alrayyes/hush-hush-python/commit/5d1269da6e6d3724eda7be14c3773e9f895cbfc1))

## [1.1.1](https://github.com/alrayyes/hush-hush-python/compare/v1.1.0...v1.1.1) (2026-08-31)


### Bug Fixes

* **ci:** don't fail CI on Codecov's Dependabot-token gap ([#15](https://github.com/alrayyes/hush-hush-python/issues/15)) ([5c65b6d](https://github.com/alrayyes/hush-hush-python/commit/5c65b6dd31bd66e1c320ff264356cf28646b7bd9))

## [1.1.0](https://github.com/alrayyes/hush-hush-python/compare/v1.0.0...v1.1.0) (2026-08-31)


### Features

* regenerate client from updated hush-hush spec ([#12](https://github.com/alrayyes/hush-hush-python/issues/12)) ([820fd98](https://github.com/alrayyes/hush-hush-python/commit/820fd982b2e4833c0b0074b9202f611418fe4095))


### Bug Fixes

* **codegen:** oasdiff never reached PATH, silently breaking classification ([#13](https://github.com/alrayyes/hush-hush-python/issues/13)) ([fc59bca](https://github.com/alrayyes/hush-hush-python/commit/fc59bcab307f9febebf6539bff5c78376c5845bf))

## [1.0.0](https://github.com/alrayyes/hush-hush-python/compare/v0.1.1...v1.0.0) (2026-08-30)


### ⚠ BREAKING CHANGES

* regenerate client from updated hush-hush spec ([#8](https://github.com/alrayyes/hush-hush-python/issues/8))

### Features

* **ci:** upload coverage to Codecov ([#10](https://github.com/alrayyes/hush-hush-python/issues/10)) ([0554292](https://github.com/alrayyes/hush-hush-python/commit/05542922e878b79726cc5cb60b4c50aa6205fff5)), closes [#9](https://github.com/alrayyes/hush-hush-python/issues/9)


### Bug Fixes

* regenerate client from updated hush-hush spec ([#8](https://github.com/alrayyes/hush-hush-python/issues/8)) ([4470e03](https://github.com/alrayyes/hush-hush-python/commit/4470e039c7772424c05748bf1b3a66e5c24444ff))

## [0.1.1](https://github.com/alrayyes/hush-hush-python/compare/v0.1.0...v0.1.1) (2026-08-30)


### Documentation

* sync openspec/tasks.md with the completed implementation checklist ([#6](https://github.com/alrayyes/hush-hush-python/issues/6)) ([ef21997](https://github.com/alrayyes/hush-hush-python/commit/ef21997a9312c31fefa0787d0ee8020741d82b4c))

## 0.1.0 (2026-08-29)


### Features

* initial scaffold for the hush-hush Python SDK ([#1](https://github.com/alrayyes/hush-hush-python/issues/1)) ([20f744f](https://github.com/alrayyes/hush-hush-python/commit/20f744fcb78377e0268a9db7e1f47712049560ba))
