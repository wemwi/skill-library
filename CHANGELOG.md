# Changelog

## [5.9.1](https://github.com/wemwi/skill-library/compare/v5.9.0...v5.9.1) (2026-07-16)


### Bug Fixes

* **selectedleafs-pos-operations:** Egress über Allowed-Hosts-Liste beschreiben, nicht über Vault-Host-Bindung ([#139](https://github.com/wemwi/skill-library/issues/139)) ([2c5a233](https://github.com/wemwi/skill-library/commit/2c5a2336754f0a5ea79e87845b775481232bc181))

## [5.9.0](https://github.com/wemwi/skill-library/compare/v5.8.0...v5.9.0) (2026-07-13)


### Features

* **global-agent-framework:** Config-Schema-Shapes, Delivery-Kontrakt & Emit-Gate; Templates auf Objektform ([#137](https://github.com/wemwi/skill-library/issues/137)) ([62e4f22](https://github.com/wemwi/skill-library/commit/62e4f22c9c8c91907071a1fafe1196bbfab22026))

## [5.8.0](https://github.com/wemwi/skill-library/compare/v5.7.0...v5.8.0) (2026-07-13)


### Features

* **selectedleafs-pos-operations:** pos-rollover-Prozedur (references/rollover.md) + Dispatch live ([#135](https://github.com/wemwi/skill-library/issues/135)) ([ab09f7d](https://github.com/wemwi/skill-library/commit/ab09f7d5fcbac15c283bd4f285cf8ad7af45a6dc))

## [5.7.0](https://github.com/wemwi/skill-library/compare/v5.6.0...v5.7.0) (2026-07-13)


### Features

* **pos-operations:** pos-salesperson v5.5.1 — email in Lexware-Kontakt ([#133](https://github.com/wemwi/skill-library/issues/133)) ([799cef7](https://github.com/wemwi/skill-library/commit/799cef769bf163188f819d3fa14c276477437706))

## [5.6.0](https://github.com/wemwi/skill-library/compare/v5.5.0...v5.6.0) (2026-07-13)


### Features

* **pos-operations:** pos-salesperson v5.5.0 — getrennte Dialog-Felder, Vertriebler-Ordner, optionale Freigabe ([#131](https://github.com/wemwi/skill-library/issues/131)) ([d17ad07](https://github.com/wemwi/skill-library/commit/d17ad07dfb74c302dac4ac5e72e125fe76214bf5))

## [5.5.0](https://github.com/wemwi/skill-library/compare/v5.4.0...v5.5.0) (2026-07-13)


### Features

* **pos-operations:** pos-salesperson Agent + Skill v5.4.0 ([#129](https://github.com/wemwi/skill-library/issues/129)) ([c98483d](https://github.com/wemwi/skill-library/commit/c98483dc72b13fe593c6a5e118dfa3619fe0d9b2))

## [5.4.0](https://github.com/wemwi/skill-library/compare/v5.3.0...v5.4.0) (2026-07-11)


### Features

* **pos-operations:** Provisions-Sheet-Template-ID in registry §2 hinterlegen ([#127](https://github.com/wemwi/skill-library/issues/127)) ([02c57fa](https://github.com/wemwi/skill-library/commit/02c57faa1a3bc5488b90456328d798a58423e169))

## [5.3.0](https://github.com/wemwi/skill-library/compare/v5.2.0...v5.3.0) (2026-07-11)


### Features

* **pos-operations:** §4.1 opening_hours multi-day 24h wrap ([#125](https://github.com/wemwi/skill-library/issues/125)) ([115836a](https://github.com/wemwi/skill-library/commit/115836ad7a4763b667ac25c0afdeb724189df02f))

## [5.2.0](https://github.com/wemwi/skill-library/compare/v5.1.1...v5.2.0) (2026-07-11)


### Features

* **pos-operations:** write Übergabeprotokolle/Bestandsprotokolle as Drive rich-link chips ([#123](https://github.com/wemwi/skill-library/issues/123)) ([c9f43bb](https://github.com/wemwi/skill-library/commit/c9f43bb3636b21fa4278c4753a0fb14567a44c82))


### Bug Fixes

* **pos-operations:** agent-bridge-Grant in store.md §5.2 auf drei Lese-Scopes präzisieren ([#122](https://github.com/wemwi/skill-library/issues/122)) ([f94a337](https://github.com/wemwi/skill-library/commit/f94a3374b1d7665886d28903d282a3c3be72fbce))

## [5.1.1](https://github.com/wemwi/skill-library/compare/v5.1.0...v5.1.1) (2026-07-10)


### Bug Fixes

* **pos-operations:** Dialog-Pflicht-vs-Kontrakt-Pflicht-Abgrenzung für assortment_list in store.md ausformuliert ([#120](https://github.com/wemwi/skill-library/issues/120)) ([ddd77f1](https://github.com/wemwi/skill-library/commit/ddd77f173146ee332afe70c95c4c66a9bee0e3a3))

## [5.1.0](https://github.com/wemwi/skill-library/compare/v5.0.0...v5.1.0) (2026-07-10)


### Features

* **pos-operations:** Feld-Kontrakt für liftr_store in store.md festschreiben ([#118](https://github.com/wemwi/skill-library/issues/118)) ([7e897a0](https://github.com/wemwi/skill-library/commit/7e897a0c5c8fc5771b27d87e4a46c0ab4618eba8))

## [5.0.0](https://github.com/wemwi/skill-library/compare/v4.0.1...v5.0.0) (2026-07-09)


### ⚠ BREAKING CHANGES

* Der POS-PARTNER-Marker am Store-Kontakt trägt jetzt die Vertriebler-Kontakt-UUID statt des Namens; registry.md §4 ist keine Wert-Tabelle mehr (Ordner-ID + Datei-Präfix entfallen ersatzlos), sondern nur noch die Marker-Konvention; der google-drive-MCP-Server ist aus der pos-invoice-Agent-Config zu entfernen.

### Features

* resolve invoice target sheet via Lexware POS-SHEET marker ([#116](https://github.com/wemwi/skill-library/issues/116)) ([44d507c](https://github.com/wemwi/skill-library/commit/44d507cfd5db5f27a79353e05f77b3a07285a6ad))

## [4.0.1](https://github.com/wemwi/skill-library/compare/v4.0.0...v4.0.1) (2026-07-09)


### Bug Fixes

* **pos-operations:** 🎉-Broadcast über telegram-broadcast, §8.3-Spalten spezifiziert ([#114](https://github.com/wemwi/skill-library/issues/114)) ([b2cfe47](https://github.com/wemwi/skill-library/commit/b2cfe4725069aacbecc7fa8d5b0b426e570be608))

## [4.0.0](https://github.com/wemwi/skill-library/compare/v3.2.0...v4.0.0) (2026-07-08)


### ⚠ BREAKING CHANGES

* the `launch` domain is renamed to `store` (references/launch.md removed; agent pos-launch → pos-store), breaking the agent allowlist referencing the old path. The v2.x invariant "no public city post" is reversed: the pos-store agent now posts exactly one 🎉 broadcast and requires send_photo on city channels.

### Features

* rename launch domain to store, add city broadcast (v3.0.0) ([#111](https://github.com/wemwi/skill-library/issues/111)) ([8360e1f](https://github.com/wemwi/skill-library/commit/8360e1f807a05f5cfd4c5197c2248366b09457ea))

## [3.2.0](https://github.com/wemwi/skill-library/compare/v3.1.0...v3.2.0) (2026-07-08)


### Features

* **global-workflow:** Repo-Writes uniform ueber Claude Code, chirurgische Ausnahme entfernt ([#109](https://github.com/wemwi/skill-library/issues/109)) ([c8827fb](https://github.com/wemwi/skill-library/commit/c8827fb79dbf1e9cbb6b57b2e187b9e142f01442))

## [3.1.0](https://github.com/wemwi/skill-library/compare/v3.0.0...v3.1.0) (2026-07-07)


### Features

* **selectedleafs-pos-operations:** pos-launch-Domäne aktiv ([#107](https://github.com/wemwi/skill-library/issues/107)) ([0e3789d](https://github.com/wemwi/skill-library/commit/0e3789d33d9ac45245dc2089b224b935d4cb20cd))

## [3.0.0](https://github.com/wemwi/skill-library/compare/v2.27.1...v3.0.0) (2026-07-07)


### ⚠ BREAKING CHANGES

* **selectedleafs-pos-operations:** Skill v2.0.0 setzt migrierte Stores!B-Keys (Lexware-Nummern) voraus; gegen ein unmigriertes JTL-Sheet läuft der §4-Match auf 0.

### Features

* **selectedleafs-pos-operations:** Store-Match auf Lexware-Kundennummer umstellen ([ce24936](https://github.com/wemwi/skill-library/commit/ce24936d56be9183cd8f5cae7d69666c4fa54e80))

## [2.27.1](https://github.com/wemwi/skill-library/compare/v2.27.0...v2.27.1) (2026-07-07)


### Bug Fixes

* **global-mcp-framework:** Secret-Naming um Cross-Consumer-Konsistenz + Nicht-MCP-Scope schärfen ([#103](https://github.com/wemwi/skill-library/issues/103)) ([edd51a1](https://github.com/wemwi/skill-library/commit/edd51a1aa8433650422e8acd845f41817193ccd2))

## [2.27.0](https://github.com/wemwi/skill-library/compare/v2.26.5...v2.27.0) (2026-07-06)


### Features

* **selectedleafs-pos-operations:** note als Wahrheitsquelle für POS-Partner + Vertriebler ([#100](https://github.com/wemwi/skill-library/issues/100)) ([5e7ff7d](https://github.com/wemwi/skill-library/commit/5e7ff7d5e1b5416981148cf20d216bdc53234f01))

## [2.26.5](https://github.com/wemwi/skill-library/compare/v2.26.4...v2.26.5) (2026-07-06)


### Bug Fixes

* **pos-operations:** Backstop-Fenster per bash statt Cron-Injektion + Lebenssignal ([#98](https://github.com/wemwi/skill-library/issues/98)) ([1bce764](https://github.com/wemwi/skill-library/commit/1bce76474d15684660ef8fc2b4c7c66b75ad14f8))

## [2.26.4](https://github.com/wemwi/skill-library/compare/v2.26.3...v2.26.4) (2026-07-06)


### Bug Fixes

* **selectedleafs-pos-operations:** invoice.md §1 auf Event-Primärpfad verzweigen ([#96](https://github.com/wemwi/skill-library/issues/96)) ([dbb10a1](https://github.com/wemwi/skill-library/commit/dbb10a11a57f2afd93582dd757d153d18f0ad153))

## [2.26.3](https://github.com/wemwi/skill-library/compare/v2.26.2...v2.26.3) (2026-07-05)


### Bug Fixes

* **selectedleafs-pos-operations:** invoice.md §1 auf uhrfreien Status-Poll umstellen ([432aa4e](https://github.com/wemwi/skill-library/commit/432aa4e400be57861f010fab3b0f8eb88fa9ee4f))

## [2.26.2](https://github.com/wemwi/skill-library/compare/v2.26.1...v2.26.2) (2026-07-03)


### Bug Fixes

* **selectedleafs-pos-operations:** invoice.md Footer-Off-by-one, Telegram-General und Dezimaltrenner korrigieren ([26acd2d](https://github.com/wemwi/skill-library/commit/26acd2d176ef1b01ae5b152296380854202a192c))

## [2.26.1](https://github.com/wemwi/skill-library/compare/v2.26.0...v2.26.1) (2026-07-03)


### Bug Fixes

* **selectedleafs-pos-operations:** Description unter 1024-Zeichen-Limit gekürzt ([c77a549](https://github.com/wemwi/skill-library/commit/c77a5494017c82e0006420615dccede713dfa48f))

## [2.26.0](https://github.com/wemwi/skill-library/compare/v2.25.0...v2.26.0) (2026-07-03)


### Features

* **selectedleafs-pos-operations:** invoice.md aus Stub migriert (Rechnung-Insert + paid-Update) ([8e98128](https://github.com/wemwi/skill-library/commit/8e981280c46d635d186820f275776d41c01c1353))

## [2.25.0](https://github.com/wemwi/skill-library/compare/v2.24.0...v2.25.0) (2026-07-01)


### Features

* **global-workflow:** harten Werkzeug-Trigger für Multi-File-Sweeps ([#85](https://github.com/wemwi/skill-library/issues/85)) ([062f7bb](https://github.com/wemwi/skill-library/commit/062f7bb9d7bcd3f71b21c2e2f05797128fe0346d))

## [2.24.0](https://github.com/wemwi/skill-library/compare/v2.23.0...v2.24.0) (2026-07-01)


### Features

* **selectedleafs-brand:** Logo-Assets in SVG/PNG-Unterordner aufteilen ([62c4443](https://github.com/wemwi/skill-library/commit/62c4443ea9f92579e562a3d051cda2cd0e572c8a))

## [2.23.0](https://github.com/wemwi/skill-library/compare/v2.22.0...v2.23.0) (2026-06-30)


### Features

* **global-agent-framework:** Manifest-Dispatch-Muster für Webhook-Brücken in §8 ([#81](https://github.com/wemwi/skill-library/issues/81)) ([d44b62d](https://github.com/wemwi/skill-library/commit/d44b62d88797cf032a59415156b3993f0813e22f))

## [2.22.0](https://github.com/wemwi/skill-library/compare/v2.21.0...v2.22.0) (2026-06-30)


### Features

* **selectedleafs-pos-operations:** inventory.md aus Stub migriert (v1.2.0) ([7568b3f](https://github.com/wemwi/skill-library/commit/7568b3f0ee3e01c391b3b36392fa804a33620a75))

## [2.21.0](https://github.com/wemwi/skill-library/compare/v2.20.3...v2.21.0) (2026-06-29)


### Features

* **selectedleafs-pos-operations:** post_message-Adressierung mit message_thread_id (v1.1.0) ([70f60a3](https://github.com/wemwi/skill-library/commit/70f60a3a4b075cd0f354f9aaf757a2207c27df41))

## [2.20.3](https://github.com/wemwi/skill-library/compare/v2.20.2...v2.20.3) (2026-06-29)


### Bug Fixes

* **selectedleafs-pos-operations:** restock.md gegen latenten KeyError + Dedupe-Fumble härten (v1.0.3) ([#74](https://github.com/wemwi/skill-library/issues/74)) ([327917a](https://github.com/wemwi/skill-library/commit/327917a92a8e1b148510d1229a2c0657927df5bc))

## [2.20.2](https://github.com/wemwi/skill-library/compare/v2.20.1...v2.20.2) (2026-06-29)


### Bug Fixes

* **pos-operations:** resumable-Upload finalisieren + google_place für Maps-Link ([#72](https://github.com/wemwi/skill-library/issues/72)) ([b590c12](https://github.com/wemwi/skill-library/commit/b590c120baaf0316876f0c51c1ef86006391fed0))

## [2.20.1](https://github.com/wemwi/skill-library/compare/v2.20.0...v2.20.1) (2026-06-29)


### Bug Fixes

* **selectedleafs-pos-operations:** tote selectedleafs-telegram-Verweise im restock-Body repointen ([157e7a9](https://github.com/wemwi/skill-library/commit/157e7a988fe0029e530257a6d71e5e155187ce7d))

## [2.20.0](https://github.com/wemwi/skill-library/compare/v2.19.0...v2.20.0) (2026-06-29)


### Features

* **selectedleafs-pos-operations:** POS-Operations-Skill konsolidieren (restock + telegram) ([0f7e634](https://github.com/wemwi/skill-library/commit/0f7e634431f398d40ca86a8fab03e3f5b96ea342))

## [2.19.0](https://github.com/wemwi/skill-library/compare/v2.18.0...v2.19.0) (2026-06-29)


### Features

* **skill:** selectedleafs-pos-restock v1.8.0 — OCR-Robustheit, GID-Auflösung, Upload-Session-Reihenfolge ([db86d0d](https://github.com/wemwi/skill-library/commit/db86d0d177826b603075377e5aa039609608c466))

## [2.18.0](https://github.com/wemwi/skill-library/compare/v2.17.0...v2.18.0) (2026-06-29)


### Features

* **global-workflow:** Skill-Updates token-effizient (§5.1) ([#67](https://github.com/wemwi/skill-library/issues/67)) ([b090282](https://github.com/wemwi/skill-library/commit/b090282018ca453f2c6e76e2af1c669bb7d14f8d))

## [2.17.0](https://github.com/wemwi/skill-library/compare/v2.16.0...v2.17.0) (2026-06-29)


### Features

* **selectedleafs-pos-restock:** Store-Lookup auf zweistufigen schlanken Query ([#65](https://github.com/wemwi/skill-library/issues/65)) ([35be3d8](https://github.com/wemwi/skill-library/commit/35be3d851e8620dda6874262068262eac59ddeb3))

## [2.16.0](https://github.com/wemwi/skill-library/compare/v2.15.0...v2.16.0) (2026-06-29)


### Features

* **selectedleafs-pos-restock:** Render zwischen OCR und Komprimierung teilen ([#63](https://github.com/wemwi/skill-library/issues/63)) ([f582aad](https://github.com/wemwi/skill-library/commit/f582aad3a73e41a18c35470d59aa9c25f7049dbd))

## [2.15.0](https://github.com/wemwi/skill-library/compare/v2.14.0...v2.15.0) (2026-06-29)


### Features

* **selectedleafs-pos-restock:** auf create_download_url + ensure_folder_path umstellen ([#61](https://github.com/wemwi/skill-library/issues/61)) ([98c9c7f](https://github.com/wemwi/skill-library/commit/98c9c7f5620a9d78817be824286f69489a11c7f7))

## [2.14.0](https://github.com/wemwi/skill-library/compare/v2.13.0...v2.14.0) (2026-06-29)


### Features

* **global-mcp-framework:** R2-presigned-Download-Pattern + R2-Naming dokumentieren ([#59](https://github.com/wemwi/skill-library/issues/59)) ([22ffc2a](https://github.com/wemwi/skill-library/commit/22ffc2aa05fd351e6d84c02c7ee9ac2852d132d3))

## [2.13.0](https://github.com/wemwi/skill-library/compare/v2.12.0...v2.13.0) (2026-06-29)


### Features

* **global-stress-test:** Skill zur Konzept-Härtung + Verdrahtung in global-workflow ([#57](https://github.com/wemwi/skill-library/issues/57)) ([b26efc8](https://github.com/wemwi/skill-library/commit/b26efc8a008bafda7b43bb407ba3fc464cd9da73))

## [2.12.0](https://github.com/wemwi/skill-library/compare/v2.11.1...v2.12.0) (2026-06-28)


### Features

* **global-agent-framework:** Kein Runtime-Install — harte Regel in §11 ([19564a3](https://github.com/wemwi/skill-library/commit/19564a392a44dbe30c320efc8ca08af71c365467))

## [2.11.1](https://github.com/wemwi/skill-library/compare/v2.11.0...v2.11.1) (2026-06-28)


### Bug Fixes

* **global-mcp-framework:** update secret naming examples — Service Account → OAuth Refresh ([3168529](https://github.com/wemwi/skill-library/commit/31685297a6d0eb7a8412db8fd2ec3781003e56f7))

## [2.11.0](https://github.com/wemwi/skill-library/compare/v2.10.0...v2.11.0) (2026-06-27)


### Features

* **selectedleafs-pos-restock:** pymupdf-Kompression + deu via tessdata.fast-deu (apt-frei) ([#51](https://github.com/wemwi/skill-library/issues/51)) ([47cab5a](https://github.com/wemwi/skill-library/commit/47cab5a1a689471c05f6daf8e457adf7ceab2451))

## [2.10.0](https://github.com/wemwi/skill-library/compare/v2.9.0...v2.10.0) (2026-06-27)


### Features

* **selectedleafs-pos-restock:** Drive-Ordnernamen als Klartext aus Metaobjekt-Feldern ([#49](https://github.com/wemwi/skill-library/issues/49)) ([53e7247](https://github.com/wemwi/skill-library/commit/53e724781037f742837d795232b17af5ca7c436c))

## [2.9.0](https://github.com/wemwi/skill-library/compare/v2.8.0...v2.9.0) (2026-06-26)


### Features

* **global-agent-framework:** §11 Egress-Kopplung, §12 Tool-Datenfluss, §13 Fail-closed (v1.5.0) ([1809e99](https://github.com/wemwi/skill-library/commit/1809e99b99b70691b40bea385dcec106654e8b2f))

## [2.8.0](https://github.com/wemwi/skill-library/compare/v2.7.0...v2.8.0) (2026-06-26)


### Features

* **selectedleafs-pos-restock:** Drive-Ablage auf Referenz-Upload umstellen (v1.2.0) ([1ab6080](https://github.com/wemwi/skill-library/commit/1ab6080311e4c1fe4756790e715e2a150a40595b))

## [2.7.0](https://github.com/wemwi/skill-library/compare/v2.6.0...v2.7.0) (2026-06-25)


### Features

* **global-workflow:** Phasengrenzen-Self-Check + Kontextwechsel-Marker ([#43](https://github.com/wemwi/skill-library/issues/43)) ([ea89f91](https://github.com/wemwi/skill-library/commit/ea89f9149ac604825612b42ec3ba443844aa6b57))

## [2.6.0](https://github.com/wemwi/skill-library/compare/v2.5.0...v2.6.0) (2026-06-25)


### Features

* **global-git-conventions:** protection.md für Repo-Härtung ergänzen ([#41](https://github.com/wemwi/skill-library/issues/41)) ([e5abd4d](https://github.com/wemwi/skill-library/commit/e5abd4d00d46c7a355cfafbf12c7bd4c6de20842))

## [2.5.0](https://github.com/wemwi/skill-library/compare/v2.4.0...v2.5.0) (2026-06-25)


### Features

* **global-workflow:** Routing um Werkzeug-Achse und Handover-Template erweitern ([66152b1](https://github.com/wemwi/skill-library/commit/66152b1be778fc575c763c5af61118a595e84836))

## [2.4.0](https://github.com/wemwi/skill-library/compare/v2.3.0...v2.4.0) (2026-06-25)


### Features

* **global-git-conventions:** settings.md hinzufügen, RELEASE_PLEASE_TOKEN korrigieren ([#34](https://github.com/wemwi/skill-library/issues/34)) ([e77f6ea](https://github.com/wemwi/skill-library/commit/e77f6ea95178584b5c13da11993ac2d48ea40e9e))

## [2.3.0](https://github.com/wemwi/skill-library/compare/v2.2.0...v2.3.0) (2026-06-25)


### Features

* **global-git-conventions:** Custom Deploy command für Multi-Worker-Repos dokumentieren ([f936ca6](https://github.com/wemwi/skill-library/commit/f936ca629478155f24748265104dd6f415a9eef6))


### Bug Fixes

* **global-workflow:** Trigger schärfen — bei jeder Nachricht zuerst lesen, kein Auto-Load ([#31](https://github.com/wemwi/skill-library/issues/31)) ([91fed8f](https://github.com/wemwi/skill-library/commit/91fed8fc377e57d5f261f01f4fa7d8127b98ba94))

## [2.2.0](https://github.com/wemwi/skill-library/compare/v2.1.1...v2.2.0) (2026-06-25)


### Features

* **global-workflow:** Workflow-Skill mit Modell-Routing ([#29](https://github.com/wemwi/skill-library/issues/29)) ([b695f39](https://github.com/wemwi/skill-library/commit/b695f39a79e66f8181366d69f15d98fdb96f3419))

## [2.1.1](https://github.com/wemwi/skill-library/compare/v2.1.0...v2.1.1) (2026-06-25)


### Bug Fixes

* **global-git-conventions:** include-component-in-tag in release-please-Configs setzen ([#27](https://github.com/wemwi/skill-library/issues/27)) ([7d62f06](https://github.com/wemwi/skill-library/commit/7d62f06f5e07cc75a83168af0afa623bf0423fc5))

## [2.1.0](https://github.com/wemwi/skill-library/compare/v2.0.0...v2.1.0) (2026-06-25)


### Features

* **global-agent-framework:** Environment-Strategie (§11) + Write-Cluster in §7 ([d2a133b](https://github.com/wemwi/skill-library/commit/d2a133bbd4ce602f3c4dc421181a392444636657))

## [2.0.0](https://github.com/wemwi/skill-library/compare/v1.5.3...v2.0.0) (2026-06-25)


### ⚠ BREAKING CHANGES

* **selectedleafs-pos-restock:** rename von selectedleafs-pos-documentation

### Code Refactoring

* **selectedleafs-pos-restock:** rename von selectedleafs-pos-documentation ([0b166d9](https://github.com/wemwi/skill-library/commit/0b166d953729b2bfb7d3068e4dc06f8877f0f66b))

## [1.5.3](https://github.com/wemwi/skill-library/compare/v1.5.2...v1.5.3) (2026-06-24)


### Bug Fixes

* **global-git-conventions:** checkout vor Release-PR-Merge ([68eb7f3](https://github.com/wemwi/skill-library/commit/68eb7f372181b7e0a140ef545aa9c1e5a00b5928))

## [1.5.2](https://github.com/wemwi/skill-library/compare/v1.5.1...v1.5.2) (2026-06-24)


### Bug Fixes

* **global-git-conventions:** release-please-action auf v5 ([1110bef](https://github.com/wemwi/skill-library/commit/1110beff66315aefe6917ca283d15b7a3fb0b2ee))

## [1.5.1](https://github.com/wemwi/skill-library/compare/v1.5.0...v1.5.1) (2026-06-24)


### Bug Fixes

* **global-git-conventions:** PAT als Repo-Secret statt org-weit ([4c882cc](https://github.com/wemwi/skill-library/commit/4c882cc4eff7b70a2e490f9ca3940fc34fa58bc2))

## [1.5.0](https://github.com/wemwi/skill-library/compare/v1.4.1...v1.5.0) (2026-06-24)


### Features

* **global-git-conventions:** Release-PRs automatisch mergen ([6dc2e9b](https://github.com/wemwi/skill-library/commit/6dc2e9b546c70dbf0550263412036e2fabf448f2))


### Bug Fixes

* MCP-Worker-Naming-Doku zurück auf &lt;service&gt;-mcp ([#17](https://github.com/wemwi/skill-library/issues/17)) ([701c7ec](https://github.com/wemwi/skill-library/commit/701c7eca2981914539a05e22c87a2f71a780da3a))

## [1.4.1](https://github.com/wemwi/skill-library/compare/v1.4.0...v1.4.1) (2026-06-24)


### Reverts

* MCP-Worker-Naming zurück auf &lt;service&gt;-mcp ([#15](https://github.com/wemwi/skill-library/issues/15)) ([ab81337](https://github.com/wemwi/skill-library/commit/ab813372228045256616a6bb238f10b9bd3b86f5))

## [1.4.0](https://github.com/wemwi/skill-library/compare/v1.3.0...v1.4.0) (2026-06-24)


### Features

* **global-agent-framework:** Least-Privilege-Muster und vollständige MCP-Config-Templates ([5363a5d](https://github.com/wemwi/skill-library/commit/5363a5d69bfd718a144a8173cd4fb7d15788d317))

## [1.3.0](https://github.com/wemwi/skill-library/compare/v1.2.0...v1.3.0) (2026-06-24)


### Features

* **global-mcp-framework:** Multi-Worker-aus-einem-Repo via Environments dokumentieren ([81ce7a8](https://github.com/wemwi/skill-library/commit/81ce7a82b2c47a5073ab2893185e10d1ebdc5240))
* **selectedleafs-pos-documentation:** Übergabeprotokoll-Auswertung für pos-restock-Agent ergänzen ([6c6e462](https://github.com/wemwi/skill-library/commit/6c6e46287aaeae895a155ffe9c10fb42387b33b7))

## [1.2.0](https://github.com/wemwi/skill-library/compare/v1.1.0...v1.2.0) (2026-06-24)


### Features

* **agent-framework:** add YAML config templates and model selection section ([afcb04a](https://github.com/wemwi/skill-library/commit/afcb04a49ac2ec202ac46910312fda06eeae5a42))

## [1.1.0](https://github.com/wemwi/skill-library/compare/v1.0.0...v1.1.0) (2026-06-23)


### Features

* **global-agent-framework:** Skill für Claude Managed Agents hinzugefügt ([733f1d1](https://github.com/wemwi/skill-library/commit/733f1d1255caca1aee3df0f7df48099ce37d9f8e))
* **global-git-conventions:** proaktiven Commit-Vorschlag + Skill-Versionssemantik ergänzen ([31214aa](https://github.com/wemwi/skill-library/commit/31214aa08e9db123db5780e15b2638b943036056))

## 1.0.0 (2026-06-22)


### Features

* **global-mcp-framework:** Consumer-Importe auf mcp-foundation-Fassade umstellen ([ad4472b](https://github.com/wemwi/skill-library/commit/ad4472b3c9658e68deb654e0e304f1285df55a01))


### Bug Fixes

* use simple release-type for release-please ([377d1eb](https://github.com/wemwi/skill-library/commit/377d1ebc32fc790d5573b22e811ef53357933edc))

## Changelog

<!--
Diese Datei wird automatisch von release-please gepflegt.
NICHT von Hand bearbeiten und KEINE [Unreleased]-Sektion einfügen —
Versionsblöcke werden beim Merge des Release-PR aus den Conventional Commits generiert.
-->
