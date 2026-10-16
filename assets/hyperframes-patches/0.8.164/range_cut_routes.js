  api.get("/pv-workbench/capabilities", (c) => c.json({ patch_id: PV_SYNC_CUT_PATCH_ID, range_cut_preview: true, atomic_commit: "native-cas-history", version: "0.8.164" }));
  api.post("/projects/:id/file-mutations/range-cut-preview", async (c) => {
    const body = await c.req.json().catch(() => null);
    if (!body || typeof body.path !== "string" || typeof body.expectedVersion !== "string") return c.json({ error: "path and expectedVersion required", patch_id: PV_SYNC_CUT_PATCH_ID }, 400);
    const project = await adapter.resolveProject(c.req.param("id"));
    if (!project) return c.json({ error: "not found" }, 404);
    const absPath = pinWithinProject(project.dir, body.path);
    if (!absPath) return c.json({ error: "forbidden path" }, 403);
    let before;
    try { before = readFileSync5(absPath, "utf-8"); }
    catch { return c.json({ error: "not found" }, 404); }
    const version = fileContentVersion(before);
    if (version !== body.expectedVersion) return c.json({ error: "file conflict", conflict: true, path: body.path, currentVersion: version, patch_id: PV_SYNC_CUT_PATCH_ID }, 409);
    try {
      const writer = resolveGsapWriter({ HYPERFRAMES_GSAP_WRITER: process.env["HYPERFRAMES_GSAP_WRITER"] });
      const result = await pvRangeCutPreviewHtml(before, body, writer);
      return c.json({ ok: true, path: body.path, before, ...result, version: fileContentVersion(result.after) });
    } catch (error) {
      return c.json({ error: error instanceof Error ? error.message : String(error), patch_id: PV_SYNC_CUT_PATCH_ID }, 400);
    }
  });
