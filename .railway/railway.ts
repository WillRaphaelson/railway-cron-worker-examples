import { defineRailway, project, service } from "railway/iac";

export default defineRailway(() => {
  const source = { repo: "WillRaphaelson/railway-cron-worker-examples", branch: "main" };
  const build = { builder: "DOCKERFILE" as const, dockerfilePath: "Dockerfile" };
  const env = { TARGET_URL: "https://example.com" };
  const cron = service("cron-check", {
    source, build, env,
    start: "python check_once.py",
    deploy: { cronSchedule: "0 9 * * *", restartPolicyType: "NEVER", sleepApplication: false },
  });
  const worker = service("worker-check", {
    source, build, env,
    start: "python worker.py",
    deploy: { restartPolicyType: "ON_FAILURE", restartPolicyMaxRetries: 10, sleepApplication: false },
  });
  return project("cron-worker-primitives", { resources: [cron, worker] });
});
