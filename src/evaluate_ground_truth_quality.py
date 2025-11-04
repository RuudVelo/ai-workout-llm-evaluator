#!/usr/bin/env python3
"""
Ground Truth Quality Evaluation Script

Analyzes ground truth workout JSON files and generates comprehensive quality reports
in HTML, Markdown, and JSON formats.

Usage:
    python src/evaluate_ground_truth_quality.py <ground_truth_folder>

Example:
    python src/evaluate_ground_truth_quality.py ground_truth/
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import Counter, defaultdict


class GroundTruthQualityEvaluator:
    """Evaluates quality of ground truth workout files."""

    def __init__(self, ground_truth_dir: Path):
        self.ground_truth_dir = ground_truth_dir
        self.files_data = []
        self.issues = []

    def load_ground_truth_files(self) -> None:
        """Load all JSON files from ground truth directory."""
        json_files = sorted(self.ground_truth_dir.glob("*.json"))

        if not json_files:
            raise ValueError(f"No JSON files found in {self.ground_truth_dir}")

        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['_file_path'] = file_path.name
                    self.files_data.append(data)
            except Exception as e:
                self.issues.append({
                    'file': file_path.name,
                    'error': f"Failed to load: {str(e)}"
                })

    def analyze_validation_results(self) -> Dict[str, Any]:
        """Analyze validation results across all files."""
        total_files = len(self.files_data)
        passed_all = 0
        validation_scores = []
        failed_metrics = defaultdict(int)

        for data in self.files_data:
            validation = data.get('validation_results', {})

            if validation.get('all_passed', False):
                passed_all += 1

            # Parse score (e.g., "7/8")
            overall_score = validation.get('overall_score', '0/0')
            if '/' in overall_score:
                passed, total = map(int, overall_score.split('/'))
                validation_scores.append({
                    'file': data['_file_path'],
                    'passed': passed,
                    'total': total,
                    'pass_rate': validation.get('pass_rate', 0)
                })

            # Track which metrics failed
            for metric in validation.get('metrics', []):
                if not metric.get('passed', True):
                    metric_name = metric.get('metric', 'unknown')
                    failed_metrics[metric_name] += 1

        return {
            'total_files': total_files,
            'passed_all_validations': passed_all,
            'pass_all_rate': (passed_all / total_files * 100) if total_files > 0 else 0,
            'validation_scores': validation_scores,
            'failed_metrics': dict(failed_metrics),
            'average_pass_rate': sum(s['pass_rate'] for s in validation_scores) / len(validation_scores) if validation_scores else 0
        }

    def analyze_workout_characteristics(self) -> Dict[str, Any]:
        """Analyze workout characteristics across all files."""
        durations = []
        interval_counts = []
        segment_types = []
        zone_times = defaultdict(int)

        for data in self.files_data:
            workout = data.get('workout', {})

            # Duration
            duration = workout.get('workout_duration', 0)
            durations.append(duration)

            # Intervals
            intervals = workout.get('intervals', [])
            interval_counts.append(len(intervals))

            # Segment types and zones
            for interval in intervals:
                seg_type = interval.get('type', 'unknown')
                segment_types.append(seg_type)

                zone = interval.get('zone', 0)
                duration = interval.get('endTimeSeconds', 0) - interval.get('startTimeSeconds', 0)
                zone_times[zone] += duration

        segment_type_dist = Counter(segment_types)

        return {
            'duration_stats': {
                'min': min(durations) if durations else 0,
                'max': max(durations) if durations else 0,
                'avg': sum(durations) / len(durations) if durations else 0,
                'distribution': Counter(durations)
            },
            'interval_stats': {
                'min': min(interval_counts) if interval_counts else 0,
                'max': max(interval_counts) if interval_counts else 0,
                'avg': sum(interval_counts) / len(interval_counts) if interval_counts else 0
            },
            'segment_type_distribution': dict(segment_type_dist),
            'zone_time_distribution': dict(sorted(zone_times.items()))
        }

    def collect_detailed_issues(self) -> List[Dict[str, Any]]:
        """Collect detailed issues from validation results."""
        detailed_issues = []

        for data in self.files_data:
            validation = data.get('validation_results', {})

            for metric in validation.get('metrics', []):
                if not metric.get('passed', True):
                    metric_name = metric.get('metric', 'unknown')

                    # Extract relevant details based on metric type
                    details_str = ''
                    if 'mismatches' in metric and metric['mismatches']:
                        details_str = f"{len(metric['mismatches'])} mismatch(es) found"
                        # Show first few mismatches
                        for mismatch in metric['mismatches'][:3]:
                            if 'segment_number' in mismatch:
                                details_str += f"\n  - Segment {mismatch.get('segment_number', '?')}"
                                if 'power' in mismatch:
                                    details_str += f": Power {mismatch.get('power')}W declared as Zone {mismatch.get('declared_zone')}, actually Zone {mismatch.get('actual_zone')}"
                                elif 'declared_percentage' in mismatch:
                                    details_str += f": Declared {mismatch.get('declared_percentage')}%, calculated {mismatch.get('calculated_percentage')}%"
                                elif 'declared_adjustment' in mismatch:
                                    details_str += f": Power adjustment error"
                    elif 'gaps' in metric and metric['gaps']:
                        details_str = f"{len(metric['gaps'])} gap(s) found in time continuity"
                    elif 'overlaps' in metric and metric['overlaps']:
                        details_str = f"{len(metric['overlaps'])} overlap(s) found in time continuity"
                    elif 'difference' in metric:
                        diff = metric['difference']
                        declared = metric.get('declared_duration', 0)
                        calculated = metric.get('calculated_duration', 0)
                        details_str = f"Duration mismatch: declared {declared}s, calculated {calculated}s (diff: {diff}s)"
                    elif 'missing_fields' in metric and metric['missing_fields']:
                        details_str = f"Missing fields: {', '.join(metric['missing_fields'])}"
                    elif 'invalid_types' in metric and metric['invalid_types']:
                        details_str = f"Invalid types: {', '.join(metric['invalid_types'])}"
                    elif 'errors' in metric and metric['errors']:
                        details_str = f"Errors: {', '.join(metric['errors'])}"

                    detailed_issues.append({
                        'file': data['_file_path'],
                        'prompt_id': data.get('prompt_id', 'unknown'),
                        'metric': metric_name,
                        'details': details_str if details_str else 'Validation failed (no details provided)',
                        'raw_metric': metric  # Keep raw data for reference
                    })

        return detailed_issues

    def generate_per_file_analysis(self) -> List[Dict[str, Any]]:
        """Generate per-file analysis data."""
        per_file = []

        for data in self.files_data:
            validation = data.get('validation_results', {})
            workout = data.get('workout', {})
            gen_metadata = data.get('generation_metadata', {})

            # Parse score
            overall_score = validation.get('overall_score', '0/0')
            passed, total = 0, 0
            if '/' in overall_score:
                passed, total = map(int, overall_score.split('/'))

            # Count issues
            issues_count = sum(1 for m in validation.get('metrics', []) if not m.get('passed', True))

            # Generation stats
            tokens_all = gen_metadata.get('total_tokens_all_attempts', {})
            attempts = gen_metadata.get('attempts', 0)
            latency = gen_metadata.get('total_latency_all_attempts', 0)
            cost = gen_metadata.get('total_cost_all_attempts', 0)
            input_tokens = tokens_all.get('input', 0)
            output_tokens = tokens_all.get('output', 0)

            per_file.append({
                'file': data['_file_path'],
                'prompt_id': data.get('prompt_id', 'unknown'),
                'validation_score': overall_score,
                'pass_rate': validation.get('pass_rate', 0),
                'duration': workout.get('workout_duration', 0),
                'intervals': len(workout.get('intervals', [])),
                'issues_count': issues_count,
                'all_passed': validation.get('all_passed', False),
                'attempts': attempts,
                'latency_ms': latency,
                'latency_sec': latency / 1000,
                'cost': cost,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': tokens_all.get('total', 0)
            })

        return sorted(per_file, key=lambda x: x['pass_rate'], reverse=True)

    def analyze_generation_metadata(self) -> Dict[str, Any]:
        """Analyze generation metadata."""
        total_input_tokens = 0
        total_output_tokens = 0
        total_tokens = 0
        total_cost = 0
        total_input_cost = 0
        total_output_cost = 0
        total_latency = 0
        model_usage = Counter()
        attempt_distribution = Counter()
        latencies = []
        costs = []
        input_tokens_list = []
        output_tokens_list = []

        for data in self.files_data:
            metadata = data.get('generation_metadata', {})

            # Tokens
            tokens_all = metadata.get('total_tokens_all_attempts', {})
            input_tok = tokens_all.get('input', 0)
            output_tok = tokens_all.get('output', 0)
            total_tok = tokens_all.get('total', 0)

            total_input_tokens += input_tok
            total_output_tokens += output_tok
            total_tokens += total_tok
            input_tokens_list.append(input_tok)
            output_tokens_list.append(output_tok)

            # Cost
            cost = metadata.get('total_cost_all_attempts', 0)
            input_cost = metadata.get('total_input_cost_all_attempts', 0)
            output_cost = metadata.get('total_output_cost_all_attempts', 0)

            total_cost += cost
            total_input_cost += input_cost
            total_output_cost += output_cost
            costs.append(cost)

            # Latency
            latency = metadata.get('total_latency_all_attempts', 0)
            total_latency += latency
            latencies.append(latency)

            # Attempts
            attempts = metadata.get('attempts', 0)
            attempt_distribution[attempts] += 1

            # Model usage
            ref_model = data.get('reference_model', {})
            model_name = ref_model.get('display_name', 'unknown')
            model_usage[model_name] += 1

        num_files = len(self.files_data) if self.files_data else 1

        return {
            'total_tokens': total_tokens,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'avg_tokens_per_workout': total_tokens / num_files,
            'avg_input_tokens_per_workout': total_input_tokens / num_files,
            'avg_output_tokens_per_workout': total_output_tokens / num_files,
            'min_input_tokens': min(input_tokens_list) if input_tokens_list else 0,
            'max_input_tokens': max(input_tokens_list) if input_tokens_list else 0,
            'min_output_tokens': min(output_tokens_list) if output_tokens_list else 0,
            'max_output_tokens': max(output_tokens_list) if output_tokens_list else 0,
            'total_cost': total_cost,
            'total_input_cost': total_input_cost,
            'total_output_cost': total_output_cost,
            'avg_cost_per_workout': total_cost / num_files,
            'avg_input_cost_per_workout': total_input_cost / num_files,
            'avg_output_cost_per_workout': total_output_cost / num_files,
            'min_cost': min(costs) if costs else 0,
            'max_cost': max(costs) if costs else 0,
            'total_latency_ms': total_latency,
            'total_latency_seconds': total_latency / 1000,
            'avg_latency_ms': total_latency / num_files,
            'avg_latency_seconds': (total_latency / num_files) / 1000,
            'min_latency_ms': min(latencies) if latencies else 0,
            'max_latency_ms': max(latencies) if latencies else 0,
            'attempt_distribution': dict(sorted(attempt_distribution.items())),
            'model_usage': dict(model_usage),
            'total_attempts': sum(attempt_distribution.keys())
        }

    def generate_report_data(self) -> Dict[str, Any]:
        """Generate comprehensive report data."""
        return {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'ground_truth_dir': str(self.ground_truth_dir),
                'total_files_analyzed': len(self.files_data)
            },
            'validation_analysis': self.analyze_validation_results(),
            'workout_characteristics': self.analyze_workout_characteristics(),
            'per_file_analysis': self.generate_per_file_analysis(),
            'detailed_issues': self.collect_detailed_issues(),
            'generation_metadata': self.analyze_generation_metadata(),
            'load_issues': self.issues
        }

    def generate_html_report(self, report_data: Dict[str, Any], output_path: Path) -> None:
        """Generate HTML report with tables and styling."""
        validation = report_data['validation_analysis']
        characteristics = report_data['workout_characteristics']
        per_file = report_data['per_file_analysis']
        issues = report_data['detailed_issues']
        gen_meta = report_data['generation_metadata']
        metadata = report_data['metadata']

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ground Truth Quality Evaluation Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header p {{
            margin: 5px 0;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }}
        .stat-card .label {{
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
        }}
        .stat-card .value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
        }}
        th:hover {{
            background-color: #5568d3;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-success {{
            background-color: #d4edda;
            color: #155724;
        }}
        .badge-warning {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .badge-danger {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .issue-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .issue-box h4 {{
            margin: 0 0 10px 0;
            color: #856404;
        }}
        .code {{
            font-family: 'Courier New', monospace;
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .recommendation {{
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Ground Truth Quality Evaluation Report</h1>
        <p><strong>Generated:</strong> {metadata['generated_at']}</p>
        <p><strong>Source Directory:</strong> {metadata['ground_truth_dir']}</p>
        <p><strong>Files Analyzed:</strong> {metadata['total_files_analyzed']}</p>
    </div>

    <!-- Executive Summary -->
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Total Files</div>
                <div class="value">{validation['total_files']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Passed All Validations</div>
                <div class="value">{validation['passed_all_validations']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Pass Rate</div>
                <div class="value">{validation['pass_all_rate']:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="label">Average Score</div>
                <div class="value">{validation['average_pass_rate']:.1f}%</div>
            </div>
        </div>
    </div>

    <!-- Validation Results Overview -->
    <div class="section">
        <h2>Validation Results Overview</h2>
        <p><strong>Files passing all validations:</strong> {validation['passed_all_validations']} / {validation['total_files']}
           ({validation['pass_all_rate']:.1f}%)</p>

        <h3>Common Validation Failures</h3>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Failure Count</th>
                </tr>
            </thead>
            <tbody>
"""

        for metric, count in sorted(validation['failed_metrics'].items(), key=lambda x: x[1], reverse=True):
            html += f"""
                <tr>
                    <td>{metric}</td>
                    <td><span class="badge badge-danger">{count}</span></td>
                </tr>
"""

        if not validation['failed_metrics']:
            html += """
                <tr>
                    <td colspan="2" style="text-align: center; color: #28a745;">No validation failures!</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>

    <!-- Per-File Analysis -->
    <div class="section">
        <h2>Per-File Analysis</h2>
        <p style="font-size: 0.9em; color: #666; margin-bottom: 15px;">
            💡 <em>Click on column headers to sort the table</em>
        </p>
        <div style="overflow-x: auto;">
            <table id="fileTable" style="min-width: 1400px;">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">Prompt ID</th>
                        <th onclick="sortTable(1)">File</th>
                        <th onclick="sortTable(2)">Score</th>
                        <th onclick="sortTable(3)">Pass Rate</th>
                        <th onclick="sortTable(4)">Duration (min)</th>
                        <th onclick="sortTable(5)">Intervals</th>
                        <th onclick="sortTable(6)">Attempts</th>
                        <th onclick="sortTable(7)">Latency (s)</th>
                        <th onclick="sortTable(8)">Cost</th>
                        <th onclick="sortTable(9)">Input Tokens</th>
                        <th onclick="sortTable(10)">Output Tokens</th>
                        <th onclick="sortTable(11)">Total Tokens</th>
                        <th onclick="sortTable(12)">Issues</th>
                        <th onclick="sortTable(13)">Status</th>
                    </tr>
                </thead>
                <tbody>
"""

        for file in per_file:
            status_badge = 'badge-success' if file['all_passed'] else 'badge-warning'
            status_text = 'PASS' if file['all_passed'] else 'ISSUES'
            duration_min = file['duration'] / 60

            html += f"""
                <tr>
                    <td>{file['prompt_id']}</td>
                    <td><span class="code">{file['file']}</span></td>
                    <td>{file['validation_score']}</td>
                    <td>{file['pass_rate']:.1f}%</td>
                    <td>{duration_min:.1f}</td>
                    <td>{file['intervals']}</td>
                    <td>{file['attempts']}</td>
                    <td>{file['latency_sec']:.2f}</td>
                    <td>${file['cost']:.4f}</td>
                    <td>{file['input_tokens']:,}</td>
                    <td>{file['output_tokens']:,}</td>
                    <td>{file['total_tokens']:,}</td>
                    <td>{file['issues_count']}</td>
                    <td><span class="badge {status_badge}">{status_text}</span></td>
                </tr>
"""

        html += """
                </tbody>
            </table>
        </div>
    </div>

    <!-- Quality Metrics Deep Dive -->
    <div class="section">
        <h2>Quality Metrics Deep Dive</h2>

        <h3>Workout Characteristics</h3>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Avg Duration</div>
                <div class="value">{:.0f} min</div>
            </div>
            <div class="stat-card">
                <div class="label">Avg Intervals</div>
                <div class="value">{:.1f}</div>
            </div>
            <div class="stat-card">
                <div class="label">Min Duration</div>
                <div class="value">{:.0f} min</div>
            </div>
            <div class="stat-card">
                <div class="label">Max Duration</div>
                <div class="value">{:.0f} min</div>
            </div>
        </div>

        <h3>Segment Type Distribution</h3>
        <table>
            <thead>
                <tr>
                    <th>Segment Type</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody>
""".format(
            characteristics['duration_stats']['avg'] / 60,
            characteristics['interval_stats']['avg'],
            characteristics['duration_stats']['min'] / 60,
            characteristics['duration_stats']['max'] / 60
        )

        for seg_type, count in sorted(characteristics['segment_type_distribution'].items(), key=lambda x: x[1], reverse=True):
            html += f"""
                <tr>
                    <td>{seg_type}</td>
                    <td>{count}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>

        <h3>Power Zone Time Distribution</h3>
        <table>
            <thead>
                <tr>
                    <th>Zone</th>
                    <th>Total Time (min)</th>
                </tr>
            </thead>
            <tbody>
"""

        for zone, time_sec in sorted(characteristics['zone_time_distribution'].items()):
            html += f"""
                <tr>
                    <td>Zone {zone}</td>
                    <td>{time_sec / 60:.1f}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>

    <!-- Issues & Anomalies -->
    <div class="section">
        <h2>Issues & Anomalies</h2>
"""

        if issues:
            html += f"<p>Found <strong>{len(issues)}</strong> validation issues across the ground truth files:</p>"
            for issue in issues:
                # Format details with line breaks for HTML
                details_html = issue['details'].replace('\n', '<br>')
                html += f"""
        <div class="issue-box">
            <h4>{issue['metric']}</h4>
            <p><strong>File:</strong> <span class="code">{issue['file']}</span></p>
            <p><strong>Prompt ID:</strong> {issue['prompt_id']}</p>
            <p><strong>Details:</strong> {details_html}</p>
        </div>
"""
        else:
            html += "<p style='color: #28a745;'>No validation issues found! All ground truth files passed validation.</p>"

        html += """
    </div>

    <!-- Statistical Summary -->
    <div class="section">
        <h2>Statistical Summary</h2>

        <h3>Generation Performance Overview</h3>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Total Tokens</div>
                <div class="value">{:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Cost</div>
                <div class="value">${:.4f}</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Latency</div>
                <div class="value">{:.1f}s</div>
            </div>
            <div class="stat-card">
                <div class="label">Avg Latency</div>
                <div class="value">{:.2f}s</div>
            </div>
        </div>

        <h3>Token Statistics</h3>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Input Tokens</th>
                    <th>Output Tokens</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Total</strong></td>
                    <td>{:,}</td>
                    <td>{:,}</td>
                    <td>{:,}</td>
                </tr>
                <tr>
                    <td><strong>Average per Workout</strong></td>
                    <td>{:.0f}</td>
                    <td>{:.0f}</td>
                    <td>{:.0f}</td>
                </tr>
                <tr>
                    <td><strong>Min</strong></td>
                    <td>{:,}</td>
                    <td>{:,}</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td><strong>Max</strong></td>
                    <td>{:,}</td>
                    <td>{:,}</td>
                    <td>-</td>
                </tr>
            </tbody>
        </table>

        <h3>Cost Breakdown</h3>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Input Cost</th>
                    <th>Output Cost</th>
                    <th>Total Cost</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Total</strong></td>
                    <td>${:.4f}</td>
                    <td>${:.4f}</td>
                    <td>${:.4f}</td>
                </tr>
                <tr>
                    <td><strong>Average per Workout</strong></td>
                    <td>${:.4f}</td>
                    <td>${:.4f}</td>
                    <td>${:.4f}</td>
                </tr>
                <tr>
                    <td><strong>Min per Workout</strong></td>
                    <td>-</td>
                    <td>-</td>
                    <td>${:.4f}</td>
                </tr>
                <tr>
                    <td><strong>Max per Workout</strong></td>
                    <td>-</td>
                    <td>-</td>
                    <td>${:.4f}</td>
                </tr>
            </tbody>
        </table>

        <h3>Latency Statistics</h3>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Latency (ms)</th>
                    <th>Latency (seconds)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Total</strong></td>
                    <td>{:,}</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td><strong>Average</strong></td>
                    <td>{:.0f}</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td><strong>Min</strong></td>
                    <td>{:,}</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td><strong>Max</strong></td>
                    <td>{:,}</td>
                    <td>{:.2f}</td>
                </tr>
            </tbody>
        </table>

        <h3>Attempt Distribution</h3>
        <table>
            <thead>
                <tr>
                    <th>Attempts</th>
                    <th>Number of Workouts</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
""".format(
            gen_meta['total_tokens'],
            gen_meta['total_cost'],
            gen_meta['total_latency_seconds'],
            gen_meta['avg_latency_seconds'],
            gen_meta['total_input_tokens'],
            gen_meta['total_output_tokens'],
            gen_meta['total_tokens'],
            gen_meta['avg_input_tokens_per_workout'],
            gen_meta['avg_output_tokens_per_workout'],
            gen_meta['avg_tokens_per_workout'],
            gen_meta['min_input_tokens'],
            gen_meta['min_output_tokens'],
            gen_meta['max_input_tokens'],
            gen_meta['max_output_tokens'],
            gen_meta['total_input_cost'],
            gen_meta['total_output_cost'],
            gen_meta['total_cost'],
            gen_meta['avg_input_cost_per_workout'],
            gen_meta['avg_output_cost_per_workout'],
            gen_meta['avg_cost_per_workout'],
            gen_meta['min_cost'],
            gen_meta['max_cost'],
            gen_meta['total_latency_ms'],
            gen_meta['total_latency_seconds'],
            gen_meta['avg_latency_ms'],
            gen_meta['avg_latency_seconds'],
            gen_meta['min_latency_ms'],
            gen_meta['min_latency_ms'] / 1000,
            gen_meta['max_latency_ms'],
            gen_meta['max_latency_ms'] / 1000
        )

        total_workouts = sum(gen_meta['attempt_distribution'].values())
        for attempts, count in gen_meta['attempt_distribution'].items():
            percentage = (count / total_workouts * 100) if total_workouts > 0 else 0
            html += f"""
                <tr>
                    <td>{attempts}</td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
"""

        html += """
            </tbody>
        </table>

        <h3>Model Usage</h3>
        <table>
            <thead>
                <tr>
                    <th>Model</th>
                    <th>Usage Count</th>
                </tr>
            </thead>
            <tbody>
"""

        for model, count in gen_meta['model_usage'].items():
            html += f"""
                <tr>
                    <td>{model}</td>
                    <td>{count}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>

    <!-- Recommendations -->
    <div class="section">
        <h2>Recommendations</h2>
"""

        files_with_issues = [f for f in per_file if not f['all_passed']]

        if files_with_issues:
            html += f"""
        <div class="recommendation">
            <h3>Files Requiring Attention</h3>
            <p>The following {len(files_with_issues)} file(s) have validation issues that should be reviewed:</p>
            <ul>
"""
            for file in files_with_issues:
                html += f"                <li><span class='code'>{file['file']}</span> - Score: {file['validation_score']} ({file['issues_count']} issue(s))</li>\n"

            html += """
            </ul>
        </div>
"""
        else:
            html += """
        <div class="recommendation">
            <h3>Excellent Quality!</h3>
            <p>All ground truth files passed validation. No immediate action required.</p>
        </div>
"""

        # Add general recommendations
        html += """
        <div class="recommendation">
            <h3>General Recommendations</h3>
            <ul>
                <li>Regularly review validation failures to maintain data quality</li>
                <li>Consider adding more diverse workout types to improve test coverage</li>
                <li>Ensure power zone calculations are accurate (most common failure point)</li>
                <li>Verify time continuity in complex workout structures</li>
            </ul>
        </div>
"""

        html += """
    </div>

    <script>
        function sortTable(columnIndex) {
            const table = document.getElementById("fileTable");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));

            const isNumeric = columnIndex >= 2 && columnIndex <= 6;

            rows.sort((a, b) => {
                let aVal = a.children[columnIndex].textContent.trim();
                let bVal = b.children[columnIndex].textContent.trim();

                if (isNumeric) {
                    aVal = parseFloat(aVal) || 0;
                    bVal = parseFloat(bVal) || 0;
                    return bVal - aVal;
                } else {
                    return aVal.localeCompare(bVal);
                }
            });

            rows.forEach(row => tbody.appendChild(row));
        }
    </script>
</body>
</html>
"""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html)

    def generate_markdown_report(self, report_data: Dict[str, Any], output_path: Path) -> None:
        """Generate Markdown report."""
        validation = report_data['validation_analysis']
        characteristics = report_data['workout_characteristics']
        per_file = report_data['per_file_analysis']
        issues = report_data['detailed_issues']
        gen_meta = report_data['generation_metadata']
        metadata = report_data['metadata']

        md = f"""# Ground Truth Quality Evaluation Report

**Generated:** {metadata['generated_at']}
**Source Directory:** `{metadata['ground_truth_dir']}`
**Files Analyzed:** {metadata['total_files_analyzed']}

---

## Executive Summary

- **Total Files:** {validation['total_files']}
- **Passed All Validations:** {validation['passed_all_validations']}
- **Overall Pass Rate:** {validation['pass_all_rate']:.1f}%
- **Average Validation Score:** {validation['average_pass_rate']:.1f}%

---

## Validation Results Overview

**Files passing all validations:** {validation['passed_all_validations']} / {validation['total_files']} ({validation['pass_all_rate']:.1f}%)

### Common Validation Failures

| Metric | Failure Count |
|--------|--------------|
"""

        if validation['failed_metrics']:
            for metric, count in sorted(validation['failed_metrics'].items(), key=lambda x: x[1], reverse=True):
                md += f"| {metric} | {count} |\n"
        else:
            md += "| *No failures* | 0 |\n"

        md += "\n---\n\n## Per-File Analysis\n\n"
        md += "| Prompt ID | File | Score | Pass Rate | Duration | Intervals | Attempts | Latency (s) | Cost | In Tokens | Out Tokens | Total Tokens | Issues | Status |\n"
        md += "|-----------|------|-------|-----------|----------|-----------|----------|-------------|------|-----------|------------|--------------|--------|--------|\n"

        for file in per_file:
            status = "✅ PASS" if file['all_passed'] else "⚠️ ISSUES"
            duration_min = file['duration'] / 60
            md += f"| {file['prompt_id']} | `{file['file']}` | {file['validation_score']} | {file['pass_rate']:.1f}% | {duration_min:.1f} min | {file['intervals']} | {file['attempts']} | {file['latency_sec']:.2f} | ${file['cost']:.4f} | {file['input_tokens']:,} | {file['output_tokens']:,} | {file['total_tokens']:,} | {file['issues_count']} | {status} |\n"

        md += "\n---\n\n## Quality Metrics Deep Dive\n\n### Workout Characteristics\n\n"
        md += f"- **Average Duration:** {characteristics['duration_stats']['avg'] / 60:.1f} minutes\n"
        md += f"- **Duration Range:** {characteristics['duration_stats']['min'] / 60:.0f} - {characteristics['duration_stats']['max'] / 60:.0f} minutes\n"
        md += f"- **Average Intervals:** {characteristics['interval_stats']['avg']:.1f}\n"
        md += f"- **Interval Range:** {characteristics['interval_stats']['min']} - {characteristics['interval_stats']['max']}\n"

        md += "\n### Segment Type Distribution\n\n"
        md += "| Segment Type | Count |\n"
        md += "|--------------|-------|\n"
        for seg_type, count in sorted(characteristics['segment_type_distribution'].items(), key=lambda x: x[1], reverse=True):
            md += f"| {seg_type} | {count} |\n"

        md += "\n### Power Zone Time Distribution\n\n"
        md += "| Zone | Total Time (min) |\n"
        md += "|------|------------------|\n"
        for zone, time_sec in sorted(characteristics['zone_time_distribution'].items()):
            md += f"| Zone {zone} | {time_sec / 60:.1f} |\n"

        md += "\n---\n\n## Issues & Anomalies\n\n"

        if issues:
            md += f"Found **{len(issues)}** validation issues:\n\n"
            for i, issue in enumerate(issues, 1):
                md += f"### Issue #{i}: {issue['metric']}\n\n"
                md += f"- **File:** `{issue['file']}`\n"
                md += f"- **Prompt ID:** {issue['prompt_id']}\n"
                md += f"- **Details:** {issue['details']}\n"
                md += "\n"
        else:
            md += "✅ **No validation issues found!** All ground truth files passed validation.\n\n"

        md += "---\n\n## Statistical Summary\n\n### Generation Performance Overview\n\n"
        md += f"- **Total Tokens:** {gen_meta['total_tokens']:,}\n"
        md += f"- **Total Cost:** ${gen_meta['total_cost']:.4f}\n"
        md += f"- **Total Latency:** {gen_meta['total_latency_seconds']:.2f} seconds\n"
        md += f"- **Average Latency:** {gen_meta['avg_latency_seconds']:.2f} seconds\n"

        md += "\n### Token Statistics\n\n"
        md += "| Metric | Input Tokens | Output Tokens | Total |\n"
        md += "|--------|--------------|---------------|-------|\n"
        md += f"| **Total** | {gen_meta['total_input_tokens']:,} | {gen_meta['total_output_tokens']:,} | {gen_meta['total_tokens']:,} |\n"
        md += f"| **Average per Workout** | {gen_meta['avg_input_tokens_per_workout']:.0f} | {gen_meta['avg_output_tokens_per_workout']:.0f} | {gen_meta['avg_tokens_per_workout']:.0f} |\n"
        md += f"| **Min** | {gen_meta['min_input_tokens']:,} | {gen_meta['min_output_tokens']:,} | - |\n"
        md += f"| **Max** | {gen_meta['max_input_tokens']:,} | {gen_meta['max_output_tokens']:,} | - |\n"

        md += "\n### Cost Breakdown\n\n"
        md += "| Metric | Input Cost | Output Cost | Total Cost |\n"
        md += "|--------|------------|-------------|------------|\n"
        md += f"| **Total** | ${gen_meta['total_input_cost']:.4f} | ${gen_meta['total_output_cost']:.4f} | ${gen_meta['total_cost']:.4f} |\n"
        md += f"| **Average per Workout** | ${gen_meta['avg_input_cost_per_workout']:.4f} | ${gen_meta['avg_output_cost_per_workout']:.4f} | ${gen_meta['avg_cost_per_workout']:.4f} |\n"
        md += f"| **Min per Workout** | - | - | ${gen_meta['min_cost']:.4f} |\n"
        md += f"| **Max per Workout** | - | - | ${gen_meta['max_cost']:.4f} |\n"

        md += "\n### Latency Statistics\n\n"
        md += "| Metric | Latency (ms) | Latency (seconds) |\n"
        md += "|--------|--------------|-------------------|\n"
        md += f"| **Total** | {gen_meta['total_latency_ms']:,} | {gen_meta['total_latency_seconds']:.2f} |\n"
        md += f"| **Average** | {gen_meta['avg_latency_ms']:.0f} | {gen_meta['avg_latency_seconds']:.2f} |\n"
        md += f"| **Min** | {gen_meta['min_latency_ms']:,} | {gen_meta['min_latency_ms']/1000:.2f} |\n"
        md += f"| **Max** | {gen_meta['max_latency_ms']:,} | {gen_meta['max_latency_ms']/1000:.2f} |\n"

        md += "\n### Attempt Distribution\n\n"
        md += "| Attempts | Number of Workouts | Percentage |\n"
        md += "|----------|-------------------|------------|\n"
        total_workouts = sum(gen_meta['attempt_distribution'].values())
        for attempts, count in gen_meta['attempt_distribution'].items():
            percentage = (count / total_workouts * 100) if total_workouts > 0 else 0
            md += f"| {attempts} | {count} | {percentage:.1f}% |\n"

        md += "\n### Model Usage\n\n"
        md += "| Model | Usage Count |\n"
        md += "|-------|-------------|\n"
        for model, count in gen_meta['model_usage'].items():
            md += f"| {model} | {count} |\n"

        md += "\n---\n\n## Recommendations\n\n"

        files_with_issues = [f for f in per_file if not f['all_passed']]

        if files_with_issues:
            md += f"### Files Requiring Attention ({len(files_with_issues)} file(s))\n\n"
            for file in files_with_issues:
                md += f"- `{file['file']}` - Score: {file['validation_score']} ({file['issues_count']} issue(s))\n"
            md += "\n"
        else:
            md += "### Excellent Quality! ✅\n\nAll ground truth files passed validation. No immediate action required.\n\n"

        md += "### General Recommendations\n\n"
        md += "1. Regularly review validation failures to maintain data quality\n"
        md += "2. Consider adding more diverse workout types to improve test coverage\n"
        md += "3. Ensure power zone calculations are accurate (most common failure point)\n"
        md += "4. Verify time continuity in complex workout structures\n"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(md)

    def generate_json_report(self, report_data: Dict[str, Any], output_path: Path) -> None:
        """Generate JSON report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)

    def run(self, output_base_dir: Path) -> None:
        """Run the complete evaluation and generate all reports."""
        print(f"Loading ground truth files from: {self.ground_truth_dir}")
        self.load_ground_truth_files()
        print(f"Loaded {len(self.files_data)} files")

        print("Analyzing ground truth quality...")
        report_data = self.generate_report_data()

        # Create timestamped run subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = output_base_dir / f"run_{timestamp}"

        print(f"Generating reports in: {run_dir}")
        run_dir.mkdir(parents=True, exist_ok=True)

        html_path = run_dir / "ground_truth_quality_report.html"
        self.generate_html_report(report_data, html_path)
        print(f"  ✓ HTML report: {html_path}")

        md_path = run_dir / "ground_truth_quality_report.md"
        self.generate_markdown_report(report_data, md_path)
        print(f"  ✓ Markdown report: {md_path}")

        json_path = run_dir / "ground_truth_quality_report.json"
        self.generate_json_report(report_data, json_path)
        print(f"  ✓ JSON report: {json_path}")

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        validation = report_data['validation_analysis']
        print(f"Total files analyzed: {validation['total_files']}")
        print(f"Passed all validations: {validation['passed_all_validations']} ({validation['pass_all_rate']:.1f}%)")
        print(f"Average pass rate: {validation['average_pass_rate']:.1f}%")

        if report_data['detailed_issues']:
            print(f"\n⚠️  Found {len(report_data['detailed_issues'])} validation issues")
        else:
            print("\n✅ No validation issues found!")

        print("="*60)

        return run_dir


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python src/evaluate_ground_truth_quality.py <ground_truth_folder>")
        print("\nExample:")
        print("  python src/evaluate_ground_truth_quality.py ground_truth/")
        sys.exit(1)

    ground_truth_dir = Path(sys.argv[1])

    if not ground_truth_dir.exists():
        print(f"Error: Directory not found: {ground_truth_dir}")
        sys.exit(1)

    if not ground_truth_dir.is_dir():
        print(f"Error: Not a directory: {ground_truth_dir}")
        sys.exit(1)

    # Output to reports/ground_truth/
    output_dir = Path("reports") / "ground_truth"

    evaluator = GroundTruthQualityEvaluator(ground_truth_dir)
    evaluator.run(output_dir)


if __name__ == "__main__":
    main()
