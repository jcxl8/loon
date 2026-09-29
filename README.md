# Loon 规则

## HaGeZi Ad Shield

Loon 插件地址：

```text
https://raw.githubusercontent.com/jcxl8/loon/main/Plugin/Hagezi_AdShield.lpx
```

GitHub Actions 每天从 HaGeZi 的三个源清单下载并转换为 Loon `[Rule]` 格式，只有规则发生变化时才提交更新。

来源：

- `ad-shield.txt`
- `ad-shield-subdomains.txt`
- `ad-shield-adblock.txt`

## Pinterest 去广告

Loon 插件地址：

```text
https://raw.githubusercontent.com/jcxl8/loon/main/Plugin/Pinterest_remove_ads_Loon.lpx
```

插件同时包含推广 Pin 的响应体清理、Pinterest 广告/跟踪域名拦截，以及 HaGeZi 规则的每日同步。

## Meta（Instagram / Facebook）去广告

Loon 插件地址：

```text
https://raw.githubusercontent.com/jcxl8/loon/main/Plugin/Meta_remove_ads_Loon.lpx
```

插件拦截 Instagram、Facebook、Meta 的广告与跟踪端点，并尝试从部分信息流 JSON 响应中移除推广对象；规则每天从 HaGeZi `pro.plus` 和 `ultimate` 清单同步。插件不会屏蔽 `graph.*`、`connect.*`、`mqtt.*` 等核心服务域名，以减少登录、信息流和图片加载异常。

## HaGeZi Ad Shield 中的 anti-AD 中文规则

`Hagezi_AdShield.lpx` 已额外远程引用 anti-AD 的 `surge2.txt` 域名集，因此安装 HaGeZi 插件后会同时获得 anti-AD 的中文广告域名规则。anti-AD 清单由其项目云端维护，不需要把十万条域名复制进 GitHub 仓库；GitHub Actions 仍每天更新 HaGeZi 本地规则。

如果已经单独启用 `anti-AD_Loon.lpx`，请关闭其中一个，避免重复加载同一份规则。

## anti-AD 通用广告拦截

Loon 插件地址：

```text
https://raw.githubusercontent.com/jcxl8/loon/main/Plugin/anti-AD_Loon.lpx
```

插件远程引用 anti-AD 的 `surge2.txt` 域名集，规则由 anti-AD 云端维护。它属于通用广告/隐私拦截清单，规模较大，建议与 Meta 专用插件分开启用，遇到误拦截时可以单独关闭。
