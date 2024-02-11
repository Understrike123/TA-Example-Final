import { useEffect } from 'react'
import { useTheme } from '@material-ui/core/styles'
import { Grid } from '@material-ui/core'
import { ColumnDataSource, Plot, LinearAxis, Grid as BokehGrid, Line } from 'react-bokeh'

const PlotComponent = ({ data }) => {
    const theme = useTheme()

    useEffect(() => {
        const dataSource = new ColumnDataSource({
            data: data
        })

        const xaxis = new LinearAxis()
        const yaxis = new LinearAxis()

        const plot = new Plot({
            x_range: xaxis.range,
            y_range: yaxis.range,
            x_axis: xaxis,
            y_axis: yaxis,
            toolbar_location: 'right'
        })

        const line = new Line({
            x: { field: 'x' },
            y: { field: 'y' },
            line_color: theme.palette.primary.main,
            line_width: 2
        })

        plot.add_glyph(line, dataSource)
        plot.add_layout(new BokehGrid({ ticker: xaxis.ticker }), 'below')

        plot.resize_layout()
        plot.render()

        return () => {
            plot.remove()
        }
    }, [data, theme])

    return (
        <Grid container spacing={2} justify="center">
            <Grid item xs={12}>
                <div id="bokeh-plot"></div>
            </Grid>
        </Grid>
    )
}

export default PlotComponent