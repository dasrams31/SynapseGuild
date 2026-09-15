import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { getGuildStatus, runCLI } from '../src/index.js';

describe('SynapseGuild Readiness Suite', () => {
  it('should return guild readiness status and welcome message', () => {
    const statusReport = getGuildStatus();
    assert.equal(statusReport.status, 'READY');
    assert.equal(statusReport.guild, 'SynapseGuild');
    assert.match(statusReport.greeting, /Welcome, adventurer!/);
    assert.ok(statusReport.timestamp);
  });

  it('should run CLI function successfully and return exit code 0', () => {
    const exitCode = runCLI();
    assert.equal(exitCode, 0);
  });
});
