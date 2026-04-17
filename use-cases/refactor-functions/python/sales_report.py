from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ReportType(Enum):
    """Valid report types."""
    SUMMARY = "summary"
    DETAILED = "detailed"
    FORECAST = "forecast"


class OutputFormat(Enum):
    """Valid output formats."""
    JSON = "json"
    HTML = "html"
    EXCEL = "excel"
    PDF = "pdf"


class GroupingOption(Enum):
    """Valid grouping options."""
    PRODUCT = "product"
    CATEGORY = "category"
    CUSTOMER = "customer"
    REGION = "region"


@dataclass
class DateRange:
    """Represents a date range."""
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.start > self.end:
            raise ValueError("Start date cannot be after end date")

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "DateRange":
        """Create DateRange from dictionary with 'start' and 'end' keys."""
        if not isinstance(data, dict) or 'start' not in data or 'end' not in data:
            raise ValueError("Date range must include 'start' and 'end' dates")
        
        try:
            start = datetime.strptime(data['start'], '%Y-%m-%d')
            end = datetime.strptime(data['end'], '%Y-%m-%d')
            return cls(start, end)
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {e}")


class SalesDataFilter:
    """Handles filtering of sales data."""

    @staticmethod
    def validate_sales_data(sales_data: List[Dict]) -> None:
        """Validate that sales data is a non-empty list."""
        if not sales_data or not isinstance(sales_data, list):
            raise ValueError("Sales data must be a non-empty list")

    @staticmethod
    def by_date_range(sales_data: List[Dict], date_range: DateRange) -> List[Dict]:
        """Filter sales data by date range."""
        filtered = []
        for sale in sales_data:
            sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
            if date_range.start <= sale_date <= date_range.end:
                filtered.append(sale)
        return filtered

    @staticmethod
    def by_criteria(sales_data: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply multiple filter criteria to sales data."""
        result = sales_data
        for key, value in filters.items():
            if isinstance(value, list):
                result = [sale for sale in result if sale.get(key) in value]
            else:
                result = [sale for sale in result if sale.get(key) == value]
        return result


class SalesMetricsCalculator:
    """Calculates various sales metrics."""

    @staticmethod
    def calculate_basic_metrics(sales_data: List[Dict]) -> Dict[str, Any]:
        """Calculate basic sales metrics."""
        if not sales_data:
            return {}

        amounts = [sale['amount'] for sale in sales_data]
        total = sum(amounts)

        return {
            'total_sales': total,
            'transaction_count': len(sales_data),
            'average_sale': total / len(sales_data),
            'max_sale': max(sales_data, key=lambda x: x['amount']),
            'min_sale': min(sales_data, key=lambda x: x['amount']),
        }

    @staticmethod
    def group_data(sales_data: List[Dict], grouping: str) -> Dict[str, Dict]:
        """Group sales data by specified field."""
        grouped = {}

        for sale in sales_data:
            key = sale.get(grouping, 'Unknown')
            if key not in grouped:
                grouped[key] = {
                    'count': 0,
                    'total': 0,
                    'items': []
                }

            grouped[key]['count'] += 1
            grouped[key]['total'] += sale['amount']
            grouped[key]['items'].append(sale)

        # Calculate averages
        for group_data in grouped.values():
            group_data['average'] = group_data['total'] / group_data['count']

        return grouped

    @staticmethod
    def calculate_forecast(sales_data: List[Dict]) -> Dict[str, Any]:
        """Calculate sales forecast based on monthly trends."""
        # Group sales by month
        monthly_sales = {}
        for sale in sales_data:
            sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
            month_key = f"{sale_date.year}-{sale_date.month:02d}"
            monthly_sales[month_key] = monthly_sales.get(month_key, 0) + sale['amount']

        if not monthly_sales:
            return {}

        # Calculate growth rates
        sorted_months = sorted(monthly_sales.keys())
        growth_rates = {}

        for i in range(1, len(sorted_months)):
            prev_month = sorted_months[i - 1]
            curr_month = sorted_months[i]
            prev_amount = monthly_sales[prev_month]
            curr_amount = monthly_sales[curr_month]

            if prev_amount > 0:
                growth_rate = ((curr_amount - prev_amount) / prev_amount) * 100
                growth_rates[curr_month] = growth_rate

        avg_growth_rate = sum(growth_rates.values()) / len(growth_rates) if growth_rates else 0

        # Project next 3 months
        forecast = SalesMetricsCalculator._project_future_months(
            sorted_months[-1], 
            monthly_sales[sorted_months[-1]], 
            avg_growth_rate
        )

        return {
            'monthly_sales': monthly_sales,
            'growth_rates': growth_rates,
            'average_growth_rate': avg_growth_rate,
            'projected_sales': forecast
        }

    @staticmethod
    def _project_future_months(last_month: str, last_amount: float, 
                              growth_rate: float, num_months: int = 3) -> Dict[str, float]:
        """Project sales for future months based on growth rate."""
        year, month = map(int, last_month.split('-'))
        forecast = {}
        current_amount = last_amount

        for _ in range(num_months):
            month += 1
            if month > 12:
                month = 1
                year += 1

            current_amount *= (1 + growth_rate / 100)
            forecast_key = f"{year}-{month:02d}"
            forecast[forecast_key] = current_amount

        return forecast


class ReportDataBuilder:
    """Builds the complete report data structure."""

    def __init__(self, sales_data: List[Dict], metrics: Dict[str, Any]):
        self.sales_data = sales_data
        self.metrics = metrics

    def build_base_report(self, report_type: str, date_range: Optional[DateRange] = None,
                         filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Build the base report structure."""
        return {
            'report_type': report_type,
            'date_generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'date_range': date_range.__dict__ if date_range else None,
            'filters': filters,
            'summary': {
                'total_sales': self.metrics['total_sales'],
                'transaction_count': self.metrics['transaction_count'],
                'average_sale': self.metrics['average_sale'],
                'max_sale': {
                    'amount': self.metrics['max_sale']['amount'],
                    'date': self.metrics['max_sale']['date'],
                    'details': self.metrics['max_sale']
                },
                'min_sale': {
                    'amount': self.metrics['min_sale']['amount'],
                    'date': self.metrics['min_sale']['date'],
                    'details': self.metrics['min_sale']
                }
            }
        }

    def add_grouping(self, report_data: Dict, grouped_data: Dict, 
                    grouping: str, total_sales: float) -> Dict:
        """Add grouping analysis to report."""
        report_data['grouping'] = {
            'by': grouping,
            'groups': {}
        }

        for key, data in grouped_data.items():
            report_data['grouping']['groups'][key] = {
                'count': data['count'],
                'total': data['total'],
                'average': data['average'],
                'percentage': (data['total'] / total_sales) * 100
            }

        return report_data

    def add_detailed_transactions(self, report_data: Dict) -> Dict:
        """Add detailed transaction information to report."""
        transactions = []

        for sale in self.sales_data:
            transaction = dict(sale)

            # Add calculated fields
            if 'tax' in sale and 'amount' in sale:
                transaction['pre_tax'] = sale['amount'] - sale['tax']

            if 'cost' in sale and 'amount' in sale:
                profit = sale['amount'] - sale['cost']
                transaction['profit'] = profit
                transaction['margin'] = (profit / sale['amount']) * 100

            transactions.append(transaction)

        report_data['transactions'] = transactions
        return report_data

    def add_forecast(self, report_data: Dict, forecast_data: Dict) -> Dict:
        """Add forecast data to report."""
        report_data['forecast'] = forecast_data
        return report_data


class ChartGenerator:
    """Generates chart data for reports."""

    @staticmethod
    def generate_sales_over_time(sales_data: List[Dict]) -> Dict[str, List]:
        """Generate chart data for sales over time."""
        date_sales = {}

        for sale in sales_data:
            date = sale['date']
            date_sales[date] = date_sales.get(date, 0) + sale['amount']

        sorted_dates = sorted(date_sales.keys())
        return {
            'labels': sorted_dates,
            'data': [date_sales[date] for date in sorted_dates]
        }

    @staticmethod
    def generate_grouping_pie_chart(grouped_data: Dict, grouping: str) -> Dict[str, List]:
        """Generate pie chart data for grouped data."""
        return {
            'labels': list(grouped_data.keys()),
            'data': [data['total'] for data in grouped_data.values()]
        }


class ReportGenerator:
    """Main report generator orchestrating all components."""

    def __init__(self):
        self.supported_report_types = {e.value for e in ReportType}
        self.supported_formats = {e.value for e in OutputFormat}

    def generate(self, sales_data: List[Dict], report_type: str = 'summary',
                date_range: Optional[Dict] = None, filters: Optional[Dict] = None,
                grouping: Optional[str] = None, include_charts: bool = False,
                output_format: str = 'json') -> Any:
        """
        Generate a comprehensive sales report.

        Args:
            sales_data: List of sales transactions
            report_type: 'summary', 'detailed', or 'forecast'
            date_range: Dict with 'start' and 'end' dates
            filters: Dict of filters to apply
            grouping: How to group data ('product', 'category', 'customer', 'region')
            include_charts: Whether to include charts/visualizations
            output_format: 'pdf', 'excel', 'html', or 'json'

        Returns:
            Report data or file path depending on output_format
        """
        # Validate inputs
        self._validate_inputs(sales_data, report_type, output_format)

        # Process date range and filters
        processed_data = self._process_data(sales_data, date_range, filters)

        if not processed_data:
            return self._handle_empty_result(output_format)

        # Calculate metrics
        metrics = SalesMetricsCalculator.calculate_basic_metrics(processed_data)

        # Build base report
        parsed_date_range = DateRange.from_dict(date_range) if date_range else None
        builder = ReportDataBuilder(processed_data, metrics)
        report = builder.build_base_report(report_type, parsed_date_range, filters)

        # Add grouping if specified
        if grouping:
            grouped_data = SalesMetricsCalculator.group_data(processed_data, grouping)
            report = builder.add_grouping(report, grouped_data, grouping, metrics['total_sales'])

        # Add type-specific data
        if report_type == ReportType.DETAILED.value:
            report = builder.add_detailed_transactions(report)

        elif report_type == ReportType.FORECAST.value:
            forecast_data = SalesMetricsCalculator.calculate_forecast(processed_data)
            report = builder.add_forecast(report, forecast_data)

        # Add charts if requested
        if include_charts:
            report['charts'] = self._generate_charts(processed_data, grouping, 
                                                     grouped_data if grouping else {})

        # Generate output
        return self._format_output(report, output_format, include_charts)

    def _validate_inputs(self, sales_data: List[Dict], report_type: str, 
                        output_format: str) -> None:
        """Validate input parameters."""
        SalesDataFilter.validate_sales_data(sales_data)

        if report_type not in self.supported_report_types:
            raise ValueError(f"Report type must be one of {self.supported_report_types}")

        if output_format not in self.supported_formats:
            raise ValueError(f"Output format must be one of {self.supported_formats}")

    def _process_data(self, sales_data: List[Dict], date_range: Optional[Dict],
                     filters: Optional[Dict]) -> List[Dict]:
        """Process and filter sales data."""
        result = sales_data

        if date_range:
            parsed_range = DateRange.from_dict(date_range)
            result = SalesDataFilter.by_date_range(result, parsed_range)

        if filters and result:
            result = SalesDataFilter.by_criteria(result, filters)

        return result

    def _generate_charts(self, sales_data: List[Dict], grouping: Optional[str],
                        grouped_data: Dict) -> Dict[str, Dict]:
        """Generate chart data."""
        charts = {}

        # Sales over time
        charts['sales_over_time'] = ChartGenerator.generate_sales_over_time(sales_data)

        # Grouping pie chart
        if grouping and grouped_data:
            chart_key = f'sales_by_{grouping}'
            charts[chart_key] = ChartGenerator.generate_grouping_pie_chart(
                grouped_data, grouping
            )

        return charts

    def _handle_empty_result(self, output_format: str) -> Any:
        """Handle case when no data matches criteria."""
        message = "No data matches the specified criteria"
        
        if output_format == OutputFormat.JSON.value:
            return {"message": message, "data": []}
        else:
            return _generate_empty_report(output_format)

    def _format_output(self, report_data: Dict, output_format: str, 
                      include_charts: bool) -> Any:
        """Format report in requested output format."""
        if output_format == OutputFormat.JSON.value:
            return report_data
        elif output_format == OutputFormat.HTML.value:
            return _generate_html_report(report_data, include_charts)
        elif output_format == OutputFormat.EXCEL.value:
            return _generate_excel_report(report_data, include_charts)
        elif output_format == OutputFormat.PDF.value:
            return _generate_pdf_report(report_data, include_charts)


# Placeholder helper functions
def _generate_empty_report(output_format: str) -> str:
    """Generate an empty report file."""
    return f"Empty report in {output_format} format"


def _generate_html_report(report_data: Dict, include_charts: bool) -> str:
    """Generate HTML report."""
    return "HTML report generated"


def _generate_excel_report(report_data: Dict, include_charts: bool) -> str:
    """Generate Excel report."""
    return "Excel report generated"


def _generate_pdf_report(report_data: Dict, include_charts: bool) -> str:
    """Generate PDF report."""
    return "PDF report generated"


# Backward-compatible function interface
def generate_sales_report(sales_data, report_type='summary', date_range=None,
                         filters=None, grouping=None, include_charts=False,
                         output_format='pdf'):
    """
    Generate a comprehensive sales report based on provided data and parameters.
    
    This is a backward-compatible wrapper around the refactored ReportGenerator class.

    Parameters:
    - sales_data: List of sales transactions
    - report_type: 'summary', 'detailed', or 'forecast'
    - date_range: Dict with 'start' and 'end' dates
    - filters: Dict of filters to apply
    - grouping: How to group data ('product', 'category', 'customer', 'region')
    - include_charts: Whether to include charts/visualizations
    - output_format: 'pdf', 'excel', 'html', or 'json'

    Returns:
    - Report data or file path depending on output_format
    """
    generator = ReportGenerator()
    return generator.generate(
        sales_data=sales_data,
        report_type=report_type,
        date_range=date_range,
        filters=filters,
        grouping=grouping,
        include_charts=include_charts,
        output_format=output_format
    )


# Example usage
if __name__ == "__main__":
    # Sample sales data
    sample_sales = [
        {'date': '2024-01-15', 'amount': 1000, 'product': 'Widget A', 'cost': 600, 'tax': 80},
        {'date': '2024-01-20', 'amount': 1500, 'product': 'Widget B', 'cost': 900, 'tax': 120},
        {'date': '2024-02-10', 'amount': 2000, 'product': 'Widget A', 'cost': 1200, 'tax': 160},
        {'date': '2024-02-15', 'amount': 1200, 'product': 'Widget C', 'cost': 700, 'tax': 96},
        {'date': '2024-03-05', 'amount': 1800, 'product': 'Widget B', 'cost': 1000, 'tax': 144},
    ]

    # Using the function interface (backward compatible)
    print("=== SUMMARY REPORT ===")
    summary = generate_sales_report(
        sample_sales,
        report_type='summary',
        grouping='product',
        output_format='json'
    )
    print(summary)

    # Using the class interface (new way)
    generator = ReportGenerator()
    print("\n=== DETAILED REPORT ===")
    detailed = generator.generate(
        sample_sales,
        report_type='detailed',
        date_range={'start': '2024-01-01', 'end': '2024-02-29'},
        output_format='json'
    )
    print(f"Transactions: {len(detailed.get('transactions', []))} records")

    # Generate forecast
    print("\n=== FORECAST REPORT ===")
    forecast = generator.generate(
        sample_sales,
        report_type='forecast',
        output_format='json'
    )
    print(f"Forecast data: {forecast.get('forecast', {}).get('projected_sales', {})}")