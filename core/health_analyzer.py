"""Vocal Health Analyzer - Analyzes vocal health metrics and generates weekly reports."""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics
import math
from utils.error_handler import log_error


class VocalHealthAnalyzer:
    """Analyzes vocal health metrics and generates personalized recommendations"""
    
    def __init__(self):
        self.grading_criteria = {
            'jitter': {'threshold': 1.0, 'points': 25, 'lower_is_better': True},
            'shimmer': {'threshold': 5.0, 'points': 25, 'lower_is_better': True},
            'hnr': {'threshold': 18.0, 'points': 25, 'lower_is_better': False},
            'strain_events': {'threshold': 5, 'points': 25, 'lower_is_better': True}
        }
    
    def calculate_health_grade(self, weekly_sessions: List[Dict]) -> Dict[str, any]:
        """Calculate health grade from weekly sessions
        
        Args:
            weekly_sessions: List of session data dictionaries
            
        Returns:
            Dict with 'grade' (A+/A/B/C/D), 'score' (0-100), 'details'
        """
        try:
            if not weekly_sessions:
                return {
                    'grade': 'N/A',
                    'score': 0,
                    'details': {'message': 'No sessions this week'}
                }
        
            # Calculate average metrics
            metrics = self._calculate_average_metrics(weekly_sessions)
        
            # Calculate score
            score = 0
            details = {}
        
            # Jitter score
            avg_jitter = metrics.get('avg_jitter', 999)
            if avg_jitter < 1.0:
                score += 25
                details['jitter'] = {'value': avg_jitter, 'status': 'excellent', 'points': 25}
            elif avg_jitter < 1.5:
                score += 15
                details['jitter'] = {'value': avg_jitter, 'status': 'good', 'points': 15}
            elif avg_jitter < 2.0:
                score += 10
                details['jitter'] = {'value': avg_jitter, 'status': 'fair', 'points': 10}
            else:
                details['jitter'] = {'value': avg_jitter, 'status': 'poor', 'points': 0}
        
            # Shimmer score
            avg_shimmer = metrics.get('avg_shimmer', 999)
            if avg_shimmer < 5.0:
                score += 25
                details['shimmer'] = {'value': avg_shimmer, 'status': 'excellent', 'points': 25}
            elif avg_shimmer < 7.0:
                score += 15
                details['shimmer'] = {'value': avg_shimmer, 'status': 'good', 'points': 15}
            elif avg_shimmer < 10.0:
                score += 10
                details['shimmer'] = {'value': avg_shimmer, 'status': 'fair', 'points': 10}
            else:
                details['shimmer'] = {'value': avg_shimmer, 'status': 'poor', 'points': 0}
        
            # HNR score
            avg_hnr = metrics.get('avg_hnr', 0)
            if avg_hnr > 18.0:
                score += 25
                details['hnr'] = {'value': avg_hnr, 'status': 'excellent', 'points': 25}
            elif avg_hnr > 15.0:
                score += 15
                details['hnr'] = {'value': avg_hnr, 'status': 'good', 'points': 15}
            elif avg_hnr > 12.0:
                score += 10
                details['hnr'] = {'value': avg_hnr, 'status': 'fair', 'points': 10}
            else:
                details['hnr'] = {'value': avg_hnr, 'status': 'poor', 'points': 0}
        
            # Strain events score
            total_strain = metrics.get('strain_events', 999)
            if total_strain < 5:
                score += 25
                details['strain_events'] = {'value': total_strain, 'status': 'excellent', 'points': 25}
            elif total_strain < 10:
                score += 15
                details['strain_events'] = {'value': total_strain, 'status': 'good', 'points': 15}
            elif total_strain < 20:
                score += 10
                details['strain_events'] = {'value': total_strain, 'status': 'fair', 'points': 10}
            else:
                details['strain_events'] = {'value': total_strain, 'status': 'poor', 'points': 0}
        
            # Determine grade
            grade = self._score_to_grade(score)
        
            return {
                'grade': grade,
                'score': score,
                'details': details,
                'metrics': metrics
            }
        except Exception as e:
            log_error(e, "VocalHealthAnalyzer.calculate_health_grade")
            return {
                'grade': 'N/A',
                'score': 0,
                'details': {'error': 'Error calculating grade'},
                'metrics': {}
            }
    
    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade"""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _calculate_average_metrics(self, sessions: List[Dict]) -> Dict[str, float]:
        """Calculate average metrics from sessions"""
        if not sessions:
            return {}
        
        jitters = []
        shimmers = []
        hnrs = []
        total_strain = 0
        
        for session in sessions:
            if session.get('avg_jitter', 0) > 0:
                jitters.append(session['avg_jitter'])
            if session.get('avg_shimmer', 0) > 0:
                shimmers.append(session['avg_shimmer'])
            if session.get('avg_hnr', 0) > 0:
                hnrs.append(session['avg_hnr'])
            total_strain += session.get('strain_events', 0)
        
        return {
            'avg_jitter': statistics.mean(jitters) if jitters else 0,
            'avg_shimmer': statistics.mean(shimmers) if shimmers else 0,
            'avg_hnr': statistics.mean(hnrs) if hnrs else 0,
            'strain_events': total_strain
        }
    
    def get_health_trends(self, all_sessions: List[Dict]) -> Dict[str, any]:
        """Get week-over-week health trends
        
        Args:
            all_sessions: All session data sorted by date
            
        Returns:
            Dict with 'this_week', 'last_week', 'trends'
        """
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)
        
        this_week = []
        last_week = []
        
        for session in all_sessions:
            session_date = session.get('start_time')
            if isinstance(session_date, str):
                try:
                    session_date = datetime.fromisoformat(session_date)
                except:
                    continue
            
            if not isinstance(session_date, datetime):
                continue
            
            if session_date >= week_ago:
                this_week.append(session)
            elif session_date >= two_weeks_ago:
                last_week.append(session)
        
        this_week_grade = self.calculate_health_grade(this_week)
        last_week_grade = self.calculate_health_grade(last_week)
        
        # Calculate trends
        trends = {}
        if last_week_grade['score'] > 0:
            trends['score_change'] = this_week_grade['score'] - last_week_grade['score']
            
            # Metric trends
            this_metrics = this_week_grade.get('metrics', {})
            last_metrics = last_week_grade.get('metrics', {})
            
            if last_metrics.get('avg_jitter', 0) > 0:
                jitter_change = ((this_metrics.get('avg_jitter', 0) - last_metrics['avg_jitter']) 
                                / last_metrics['avg_jitter'] * 100)
                trends['jitter_change'] = jitter_change
            
            if last_metrics.get('avg_shimmer', 0) > 0:
                shimmer_change = ((this_metrics.get('avg_shimmer', 0) - last_metrics['avg_shimmer']) 
                                 / last_metrics['avg_shimmer'] * 100)
                trends['shimmer_change'] = shimmer_change
            
            if last_metrics.get('avg_hnr', 0) > 0:
                hnr_change = ((this_metrics.get('avg_hnr', 0) - last_metrics['avg_hnr']) 
                             / last_metrics['avg_hnr'] * 100)
                trends['hnr_change'] = hnr_change
        
        return {
            'this_week': this_week_grade,
            'last_week': last_week_grade,
            'trends': trends,
            'session_counts': {
                'this_week': len(this_week),
                'last_week': len(last_week)
            }
        }
    
    def generate_recommendations(self, grade_data: Dict, trend_data: Dict = None) -> List[str]:
        """Generate personalized health recommendations
        
        Args:
            grade_data: Output from calculate_health_grade
            trend_data: Optional output from get_health_trends
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        details = grade_data.get('details', {})
        trends = trend_data.get('trends', {}) if trend_data else {}
        
        # Jitter recommendations
        jitter_info = details.get('jitter', {})
        if jitter_info.get('status') == 'poor':
            recommendations.append("⚠️ High jitter detected - Consider reducing vocal intensity and taking more rest breaks")
        elif jitter_info.get('status') == 'fair':
            recommendations.append("💡 Jitter could be improved - Focus on steady, controlled voice production")
        elif jitter_info.get('status') == 'excellent':
            recommendations.append("✅ Excellent jitter control - Keep up the steady voice production!")
        
        if trends.get('jitter_change', 0) > 15:
            recommendations.append(f"📈 Your jitter increased {trends['jitter_change']:.1f}% - Consider more rest days")
        
        # Shimmer recommendations
        shimmer_info = details.get('shimmer', {})
        if shimmer_info.get('status') == 'poor':
            recommendations.append("⚠️ High shimmer detected - Work on consistent breath support")
        elif shimmer_info.get('status') == 'fair':
            recommendations.append("💡 Shimmer could be improved - Practice steady airflow exercises")
        elif shimmer_info.get('status') == 'excellent':
            recommendations.append("✅ Excellent amplitude control - Your breath support is strong!")
        
        # HNR recommendations
        hnr_info = details.get('hnr', {})
        if hnr_info.get('status') == 'poor':
            recommendations.append("⚠️ Low harmonic-to-noise ratio - Reduce background noise or vocal strain")
        elif hnr_info.get('status') == 'fair':
            recommendations.append("💡 HNR could be improved - Focus on clear, clean vocal production")
        elif hnr_info.get('status') == 'excellent':
            recommendations.append("✅ Excellent HNR this week - Your voice clarity is outstanding!")
        
        if trends.get('hnr_change', 0) > 10:
            recommendations.append("📈 HNR improving nicely - Your vocal health is trending upward!")
        
        # Strain recommendations
        strain_info = details.get('strain_events', {})
        if strain_info.get('status') == 'poor':
            recommendations.append("⚠️ High strain events - Try shorter sessions and lower intensity training")
        elif strain_info.get('status') == 'fair':
            recommendations.append("💡 Some strain detected - You tend to strain after 20 minutes, consider breaks")
        elif strain_info.get('status') == 'excellent':
            recommendations.append("✅ Minimal strain this week - You're training safely!")
        
        # Session count recommendations
        if trend_data:
            session_counts = trend_data.get('session_counts', {})
            this_week_count = session_counts.get('this_week', 0)
            
            if this_week_count < 3:
                recommendations.append("📅 Try to practice 3-5 times per week for optimal progress")
            elif this_week_count > 7:
                recommendations.append("🛑 You're practicing a lot - Make sure to schedule rest days")
        
        # Overall grade recommendations
        grade = grade_data.get('grade')
        if grade in ['A+', 'A']:
            recommendations.append("Outstanding vocal health - Keep up your current training approach")
        elif grade in ['C', 'D', 'F']:
            recommendations.append("Your vocal health needs attention - Consider consulting a voice specialist")
        
        return recommendations[:5]  # Return top 5 recommendations

    def calculate_recommended_rest(self, all_sessions: List[Dict], fatigue_trend: Dict = None) -> Dict[str, any]:
        """Calculate recommended rest period before next session
        
        Args:
            all_sessions: All session data sorted by date
            fatigue_trend: Optional fatigue trend data from session_manager
            
        Returns:
            dict with hours_until_ready, status, reason
        """
        if not all_sessions:
            return {
                'hours_until_ready': 0,
                'status': 'ready',
                'reason': 'No previous sessions - ready to begin'
            }
        
        now = datetime.now()
        
        # Get last session
        last_session = all_sessions[-1]
        last_session_date = last_session.get('date')
        if isinstance(last_session_date, str):
            try:
                last_session_date = datetime.fromisoformat(last_session_date)
            except:
                last_session_date = now
        
        hours_since_last = (now - last_session_date).total_seconds() / 3600
        
        # Get recent sessions (last 7 days)
        week_ago = now - timedelta(days=7)
        recent_sessions = [
            s for s in all_sessions
            if datetime.fromisoformat(s['date']) >= week_ago
        ]
        
        # Count consecutive training days
        consecutive_days = self._count_consecutive_days(all_sessions)
        
        # Calculate rest need score (0-100, higher = more rest needed)
        rest_need = 0
        reasons = []
        
        # Factor 1: Recent strain events (max 30 points)
        recent_strain = sum(s.get('strain_events', 0) for s in recent_sessions[-3:])
        if recent_strain > 20:
            rest_need += 30
            reasons.append(f'High strain events ({recent_strain})')
        elif recent_strain > 10:
            rest_need += 15
            reasons.append(f'Moderate strain events ({recent_strain})')
        
        # Factor 2: Fatigue trend (max 30 points)
        if fatigue_trend:
            current_fatigue = fatigue_trend.get('current_fatigue', 0)
            trend = fatigue_trend.get('trend', 'stable')
            
            if current_fatigue > 70:
                rest_need += 30
                reasons.append(f'High fatigue ({current_fatigue:.0f}/100)')
            elif current_fatigue > 50:
                rest_need += 15
                reasons.append(f'Moderate fatigue ({current_fatigue:.0f}/100)')
            
            if trend == 'worsening':
                rest_need += 10
                reasons.append('Fatigue trend worsening')
        
        # Factor 3: Consecutive training days (max 25 points)
        if consecutive_days >= 7:
            rest_need += 25
            reasons.append(f'{consecutive_days} consecutive training days')
        elif consecutive_days >= 5:
            rest_need += 15
            reasons.append(f'{consecutive_days} consecutive training days')
        elif consecutive_days >= 3:
            rest_need += 5
        
        # Factor 4: Last session metrics (max 15 points)
        last_jitter = last_session.get('avg_jitter', 0)
        last_hnr = last_session.get('avg_hnr', 20)
        
        if last_jitter > 2.0 or last_hnr < 12:
            rest_need += 15
            reasons.append('Poor vocal quality in last session')
        elif last_jitter > 1.5 or last_hnr < 15:
            rest_need += 8
        
        # Calculate recommended hours
        if rest_need >= 70:
            hours_needed = 48  # Full 2-day rest
            status = 'rest_needed'
        elif rest_need >= 50:
            hours_needed = 24  # Full day rest
            status = 'rest_recommended'
        elif rest_need >= 30:
            hours_needed = 12  # Half day rest
            status = 'caution'
        elif rest_need >= 15:
            hours_needed = 6  # Short rest
            status = 'light_caution'
        else:
            hours_needed = 0
            status = 'ready'
        
        # Check if enough time has passed
        hours_until_ready = max(0, hours_needed - hours_since_last)
        
        if hours_until_ready == 0:
            return {
                'hours_until_ready': 0,
                'status': 'ready',
                'reason': 'Sufficient rest achieved',
                'rest_need_score': rest_need
            }
        else:
            reason = ' | '.join(reasons) if reasons else 'Recommended rest period'
            return {
                'hours_until_ready': math.ceil(hours_until_ready),
                'status': status,
                'reason': reason,
                'rest_need_score': rest_need
            }

    def calculate_recovery_score(self, previous_session: Dict, current_metrics: Dict) -> Dict[str, any]:
        """Calculate voice recovery score comparing previous session to current metrics
        
        Args:
            previous_session: Previous session data dict
            current_metrics: Current session metrics (avg_jitter, avg_shimmer, avg_hnr, strain_events)
            
        Returns:
            dict with score (0-100), status, details
        """
        if not previous_session or not current_metrics:
            return {
                'score': 100,
                'status': 'no_baseline',
                'details': {}
            }
        
        recovery_score = 100
        details = {}
        
        # Jitter recovery (max -25 points)
        prev_jitter = previous_session.get('avg_jitter', 0)
        curr_jitter = current_metrics.get('avg_jitter', 0)
        
        if prev_jitter > 0:
            jitter_improvement = ((prev_jitter - curr_jitter) / prev_jitter) * 100
            details['jitter_improvement'] = jitter_improvement
            
            if jitter_improvement < -20:  # Worse by 20%+
                recovery_score -= 25
                details['jitter_status'] = 'poor_recovery'
            elif jitter_improvement < -10:
                recovery_score -= 15
                details['jitter_status'] = 'partial_recovery'
            elif jitter_improvement < 0:
                recovery_score -= 5
                details['jitter_status'] = 'minimal_recovery'
            else:
                details['jitter_status'] = 'improved'
        
        # HNR recovery (max -25 points)
        prev_hnr = previous_session.get('avg_hnr', 20)
        curr_hnr = current_metrics.get('avg_hnr', 20)
        
        if prev_hnr > 0:
            hnr_improvement = ((curr_hnr - prev_hnr) / prev_hnr) * 100
            details['hnr_improvement'] = hnr_improvement
            
            if hnr_improvement < -15:  # Worse by 15%+
                recovery_score -= 25
                details['hnr_status'] = 'poor_recovery'
            elif hnr_improvement < -8:
                recovery_score -= 15
                details['hnr_status'] = 'partial_recovery'
            elif hnr_improvement < 0:
                recovery_score -= 5
                details['hnr_status'] = 'minimal_recovery'
            else:
                details['hnr_status'] = 'improved'
        
        # Shimmer recovery (max -20 points)
        prev_shimmer = previous_session.get('avg_shimmer', 0)
        curr_shimmer = current_metrics.get('avg_shimmer', 0)
        
        if prev_shimmer > 0:
            shimmer_improvement = ((prev_shimmer - curr_shimmer) / prev_shimmer) * 100
            details['shimmer_improvement'] = shimmer_improvement
            
            if shimmer_improvement < -20:
                recovery_score -= 20
                details['shimmer_status'] = 'poor_recovery'
            elif shimmer_improvement < -10:
                recovery_score -= 12
                details['shimmer_status'] = 'partial_recovery'
            elif shimmer_improvement < 0:
                recovery_score -= 5
                details['shimmer_status'] = 'minimal_recovery'
            else:
                details['shimmer_status'] = 'improved'
        
        # Strain event reduction (max -30 points)
        prev_strain = previous_session.get('strain_events', 0)
        curr_strain = current_metrics.get('strain_events', 0)
        
        strain_change = curr_strain - prev_strain
        details['strain_change'] = strain_change
        
        if strain_change > 10:
            recovery_score -= 30
            details['strain_status'] = 'increased_significantly'
        elif strain_change > 5:
            recovery_score -= 20
            details['strain_status'] = 'increased'
        elif strain_change > 0:
            recovery_score -= 10
            details['strain_status'] = 'slightly_increased'
        else:
            details['strain_status'] = 'reduced_or_stable'
        
        # Determine overall status
        if recovery_score >= 90:
            status = 'excellent_recovery'
        elif recovery_score >= 75:
            status = 'good_recovery'
        elif recovery_score >= 60:
            status = 'fair_recovery'
        elif recovery_score >= 40:
            status = 'poor_recovery'
        else:
            status = 'needs_attention'
        
        return {
            'score': max(0, recovery_score),
            'status': status,
            'details': details
        }

    def _count_consecutive_days(self, all_sessions: List[Dict]) -> int:
        """Count consecutive training days"""
        if not all_sessions:
            return 0
        
        today = datetime.now().date()
        consecutive = 0
        
        # Get unique training dates
        training_dates = set()
        for session in all_sessions:
            try:
                session_date = datetime.fromisoformat(session['date']).date()
                training_dates.add(session_date)
            except:
                continue
        
        # Count backwards from today
        check_date = today
        while check_date in training_dates:
            consecutive += 1
            check_date -= timedelta(days=1)
        
        return consecutive
    
    def get_monthly_health_trends(self, all_sessions: List[Dict], months: int = 6) -> Dict[str, any]:
        """Get monthly health trends for long-term analysis
        
        Args:
            all_sessions: All session data sorted by date
            months: Number of months to analyze (default 6)
            
        Returns:
            Dict with monthly averages and trends for each metric
        """
        if not all_sessions:
            return {
                'months': [],
                'monthly_data': {},
                'overall_trend': 'no_data'
            }
        
        now = datetime.now()
        monthly_data = {}
        
        # Group sessions by month
        for session in all_sessions:
            session_date = session.get('start_time') or session.get('date')
            if isinstance(session_date, str):
                try:
                    session_date = datetime.fromisoformat(session_date)
                except:
                    continue
            
            if not isinstance(session_date, datetime):
                continue
            
            # Check if session is within the requested timeframe
            months_diff = (now.year - session_date.year) * 12 + (now.month - session_date.month)
            if months_diff >= months:
                continue
            
            # Create month key (YYYY-MM)
            month_key = session_date.strftime('%Y-%m')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'sessions': [],
                    'month_name': session_date.strftime('%B %Y')
                }
            
            monthly_data[month_key]['sessions'].append(session)
        
        # Calculate averages for each month
        results = {
            'months': [],
            'monthly_data': {},
            'trends': {}
        }
        
        for month_key in sorted(monthly_data.keys()):
            month_sessions = monthly_data[month_key]['sessions']
            month_name = monthly_data[month_key]['month_name']
            
            # Calculate monthly averages
            metrics = self._calculate_average_metrics(month_sessions)
            grade = self.calculate_health_grade(month_sessions)
            
            results['months'].append(month_key)
            results['monthly_data'][month_key] = {
                'month_name': month_name,
                'session_count': len(month_sessions),
                'avg_jitter': metrics.get('avg_jitter', 0),
                'avg_shimmer': metrics.get('avg_shimmer', 0),
                'avg_hnr': metrics.get('avg_hnr', 0),
                'total_strain': metrics.get('strain_events', 0),
                'health_grade': grade.get('grade', 'N/A'),
                'health_score': grade.get('score', 0)
            }
        
        # Calculate overall trends
        if len(results['months']) >= 2:
            results['trends'] = self._calculate_long_term_trends(results['monthly_data'], results['months'])
        
        return results
    
    def get_yearly_health_overview(self, all_sessions: List[Dict]) -> Dict[str, any]:
        """Get yearly health overview for long-term tracking
        
        Args:
            all_sessions: All session data
            
        Returns:
            Dict with yearly statistics and comparisons
        """
        if not all_sessions:
            return {
                'years': [],
                'yearly_data': {},
                'best_year': None,
                'improvement_rate': 0
            }
        
        yearly_data = {}
        
        # Group sessions by year
        for session in all_sessions:
            session_date = session.get('start_time') or session.get('date')
            if isinstance(session_date, str):
                try:
                    session_date = datetime.fromisoformat(session_date)
                except:
                    continue
            
            if not isinstance(session_date, datetime):
                continue
            
            year_key = session_date.strftime('%Y')
            
            if year_key not in yearly_data:
                yearly_data[year_key] = []
            
            yearly_data[year_key].append(session)
        
        # Calculate yearly statistics
        results = {
            'years': [],
            'yearly_data': {},
            'best_year': None,
            'best_score': 0
        }
        
        for year_key in sorted(yearly_data.keys()):
            year_sessions = yearly_data[year_key]
            
            # Calculate yearly averages
            metrics = self._calculate_average_metrics(year_sessions)
            grade = self.calculate_health_grade(year_sessions)
            
            # Calculate monthly breakdown for the year
            monthly_breakdown = {}
            for session in year_sessions:
                session_date = session.get('start_time') or session.get('date')
                if isinstance(session_date, str):
                    session_date = datetime.fromisoformat(session_date)
                month = session_date.strftime('%B')
                monthly_breakdown[month] = monthly_breakdown.get(month, 0) + 1
            
            year_data = {
                'total_sessions': len(year_sessions),
                'avg_jitter': metrics.get('avg_jitter', 0),
                'avg_shimmer': metrics.get('avg_shimmer', 0),
                'avg_hnr': metrics.get('avg_hnr', 0),
                'total_strain': metrics.get('strain_events', 0),
                'health_grade': grade.get('grade', 'N/A'),
                'health_score': grade.get('score', 0),
                'monthly_breakdown': monthly_breakdown,
                'most_active_month': max(monthly_breakdown, key=monthly_breakdown.get) if monthly_breakdown else 'N/A'
            }
            
            results['years'].append(year_key)
            results['yearly_data'][year_key] = year_data
            
            # Track best year
            if year_data['health_score'] > results['best_score']:
                results['best_score'] = year_data['health_score']
                results['best_year'] = year_key
        
        # Calculate improvement rate (year-over-year)
        if len(results['years']) >= 2:
            first_year_score = results['yearly_data'][results['years'][0]]['health_score']
            last_year_score = results['yearly_data'][results['years'][-1]]['health_score']
            
            if first_year_score > 0:
                results['improvement_rate'] = ((last_year_score - first_year_score) / first_year_score) * 100
            else:
                results['improvement_rate'] = 0
        
        return results
    
    def _calculate_long_term_trends(self, monthly_data: Dict, month_keys: List[str]) -> Dict[str, any]:
        """Calculate long-term trends from monthly data
        
        Args:
            monthly_data: Dict of monthly averages
            month_keys: Sorted list of month keys
            
        Returns:
            Dict with trend analysis for each metric
        """
        if len(month_keys) < 2:
            return {}
        
        # Get first and last month data
        first_month = monthly_data[month_keys[0]]
        last_month = monthly_data[month_keys[-1]]
        
        trends = {}
        
        # Jitter trend
        if first_month['avg_jitter'] > 0:
            jitter_change = ((last_month['avg_jitter'] - first_month['avg_jitter']) / 
                           first_month['avg_jitter']) * 100
            trends['jitter'] = {
                'change_percent': jitter_change,
                'direction': 'improving' if jitter_change < 0 else 'worsening',
                'first_value': first_month['avg_jitter'],
                'last_value': last_month['avg_jitter']
            }
        
        # Shimmer trend
        if first_month['avg_shimmer'] > 0:
            shimmer_change = ((last_month['avg_shimmer'] - first_month['avg_shimmer']) / 
                            first_month['avg_shimmer']) * 100
            trends['shimmer'] = {
                'change_percent': shimmer_change,
                'direction': 'improving' if shimmer_change < 0 else 'worsening',
                'first_value': first_month['avg_shimmer'],
                'last_value': last_month['avg_shimmer']
            }
        
        # HNR trend
        if first_month['avg_hnr'] > 0:
            hnr_change = ((last_month['avg_hnr'] - first_month['avg_hnr']) / 
                        first_month['avg_hnr']) * 100
            trends['hnr'] = {
                'change_percent': hnr_change,
                'direction': 'improving' if hnr_change > 0 else 'worsening',
                'first_value': first_month['avg_hnr'],
                'last_value': last_month['avg_hnr']
            }
        
        # Overall health score trend
        if first_month['health_score'] > 0:
            score_change = ((last_month['health_score'] - first_month['health_score']) / 
                          first_month['health_score']) * 100
            trends['overall_health'] = {
                'change_percent': score_change,
                'direction': 'improving' if score_change > 0 else 'worsening',
                'first_value': first_month['health_score'],
                'last_value': last_month['health_score']
            }
        
        # Session frequency trend
        avg_early_sessions = statistics.mean([monthly_data[k]['session_count'] 
                                             for k in month_keys[:len(month_keys)//2]])
        avg_recent_sessions = statistics.mean([monthly_data[k]['session_count'] 
                                              for k in month_keys[len(month_keys)//2:]])
        
        trends['session_frequency'] = {
            'avg_early': avg_early_sessions,
            'avg_recent': avg_recent_sessions,
            'direction': 'increasing' if avg_recent_sessions > avg_early_sessions else 'decreasing'
        }
        
        return trends
