# API Documentation

### Building Documentation

In order to build this documentation, run the following command from your Toolkit Core location

```
> python /path/to/tk-core/docs/make_docs.py --version=v1.2.3 --bundle=/path/to/tk-framework-xyz/docs
```

This will build an html distribution of the docs in `/path/to/tk-framework-xyz/docs/build`.

### Uploading to github

The documentation is stored in a `gh-pages` branch in github which is then automatically reflected in github as https://shotgunsoftware.github.io/tk-framework-qtwidgets

Once you have built and previewed your documentation, simply upload it to this branch to make it public.
