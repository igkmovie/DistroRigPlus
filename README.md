## DistroRigPlus

Vroid/VRM/PMXなどの配布モデルにリグを追加するためのアドオンです。（α版はVroidのみ）その特徴は、モデルのアーマチュアにリグを追加するのではなく、専用のRigPlusを作成することです。Blenderの標準的なRigifyとは異なり、Unityなどの他のツールにインポートする際に不要なボーンを生成しません。

## α2版対応状況

- 体幹リグ・腕IK・足IK・つま先かかとリグを追加
- VRM0系のみ対応(すべてのVRM0.x系が正しく動くわけではありません)
- VRMA出力対応
- FBXベイクアニメーション対応
- BVH出力
- VRM非対応
- PMX非対応

## 配布先

[BOOTH - The International Indie Art Marketplace](https://igk.booth.pm)

## 動作環境

- Blender 3.6対応
  - 4.0非対応、今後対応予定
- VRM Add-on for Blender必須

[VRM Add-on for Blender](https://github.com/saturday06/VRM-Addon-for-Blender)

## 導入方法

1. **必要なアドオンをインストール**:
   - VRM Add-on for Blender を GitHub からダウンロードし、インストールします。
   - DistroRigPlus アドオンをインストールします。

2. **モデルの準備**:
   - VroidやVRM形式のモデルをBlenderにインポートします。
   - アーマチュアとメッシュが正しくインポートされていることを確認します。

3. **RigPlusの作成**:
   - `DistroRigPlus` タブから `Create RigPlus` をクリックし、リグを生成します。
   - 必要に応じて、リグの調整を行います。
